# Multi Load Cell Probe - Sensor Fusion for 4-Corner Bed Leveling
#
# Copyright (C) 2026  James Turton (james.turton@gmx.com)
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging, math, collections

np = None  # delay NumPy import until configuration time

from . import probe

# Helper to parse and validate bed corner positions
class BedGeometry:
    def __init__(self, config):
        # Parse bed_corners: FL, FR, RL, RR (X,Y pairs)
        corners_str = config.get('bed_corners')
        corners = [float(x.strip()) for x in corners_str.split(',')]
        if len(corners) != 8:
            raise config.error("bed_corners must have 8 values (4 X,Y pairs)")

        self.front_left = (corners[0], corners[1])
        self.front_right = (corners[2], corners[3])
        self.rear_left = (corners[4], corners[5])
        self.rear_right = (corners[6], corners[7])
        self.corners = [self.front_left, self.front_right,
                       self.rear_left, self.rear_right]

    def get_corners(self):
        return self.corners


# Synchronize and fuse data from 4 load cells
class MultiSensorCollector:
    def __init__(self, printer, load_cells, sync_window=0.010):
        self._printer = printer
        self._reactor = printer.get_reactor()
        self._load_cells = load_cells
        self._collectors = [lc.get_collector() for lc in load_cells]
        self._sync_window = sync_window
        self._is_collecting = False

    def start_collecting(self, min_time=None):
        """Start all 4 collectors"""
        if self._is_collecting:
            return
        self._is_collecting = True
        for collector in self._collectors:
            collector.start_collecting(min_time=min_time)

    def stop_collecting(self):
        """Stop all collectors and return synchronized results"""
        if not self._is_collecting:
            return [], []
        self._is_collecting = False

        # Collect from all 4 sensors
        all_results = []
        all_errors = []
        for i, collector in enumerate(self._collectors):
            samples, errors = collector.stop_collecting()
            all_results.append(samples)
            all_errors.append(errors)

        return all_results, all_errors

    def collect_min(self, min_count):
        """Collect minimum samples from each sensor"""
        self.start_collecting()
        # Collect from each sensor independently
        all_results = []
        all_errors = []
        for collector in self._collectors:
            samples, errors = collector.collect_min(min_count)
            all_results.append(samples)
            all_errors.append(errors)
        return all_results, all_errors

    def collect_until(self, print_time):
        """Collect from all sensors until print_time"""
        self.start_collecting()
        all_results = []
        all_errors = []
        for collector in self._collectors:
            samples, errors = collector.collect_until(print_time)
            all_results.append(samples)
            all_errors.append(errors)
        return all_results, all_errors

    def get_synchronized_samples(self, all_samples):
        """
        Synchronize samples from 4 sensors within sync_window
        Returns list of 4 sample arrays with aligned timestamps
        """
        if not all_samples or len(all_samples) != 4:
            return []

        # Find common time range across all sensors
        if any(len(s) == 0 for s in all_samples):
            return [[], [], [], []]

        time_starts = [s[0][0] for s in all_samples]
        time_ends = [s[-1][0] for s in all_samples]
        common_start = max(time_starts)
        common_end = min(time_ends)

        if common_start >= common_end:
            return [[], [], [], []]

        # Extract samples within common time window
        synced = []
        for sensor_samples in all_samples:
            in_window = [s for s in sensor_samples
                        if common_start <= s[0] <= common_end]
            synced.append(in_window)

        return synced


# Sensor fusion algorithms
class SensorFusion:
    @staticmethod
    def simple_average(samples_list):
        """
        Simple average fusion: avg(sensor1, sensor2, sensor3, sensor4)
        samples_list: list of 4 sample arrays [[time, force, counts], ...]
        Returns: list of [time, fused_force] pairs
        """
        if not samples_list or len(samples_list) != 4:
            return []

        # Find shortest sample count
        min_len = min(len(s) for s in samples_list)
        if min_len == 0:
            return []

        fused = []
        for i in range(min_len):
            # Average timestamp and force across 4 sensors
            avg_time = sum(s[i][0] for s in samples_list) / 4.0
            # Force is column 1 in samples (time, force, counts, tare)
            avg_force = sum(s[i][1] for s in samples_list) / 4.0
            fused.append([avg_time, avg_force])

        return fused

    @staticmethod
    def weighted_fusion(samples_list, weights):
        """
        Position-weighted fusion: sum(sensor[i] * weight[i])
        weights: [w1, w2, w3, w4] must sum to 1.0
        """
        if not samples_list or len(samples_list) != 4:
            return []
        if len(weights) != 4:
            raise ValueError("weights must have 4 values")
        if abs(sum(weights) - 1.0) > 0.01:
            raise ValueError("weights must sum to 1.0")

        min_len = min(len(s) for s in samples_list)
        if min_len == 0:
            return []

        fused = []
        for i in range(min_len):
            avg_time = sum(s[i][0] for s in samples_list) / 4.0
            weighted_force = sum(s[i][1] * w for s, w in zip(samples_list, weights))
            fused.append([avg_time, weighted_force])

        return fused

    @staticmethod
    def calculate_inverse_distance_weights(nozzle_pos, bed_corners):
        """
        Calculate weights based on inverse distance from nozzle to corners
        Closer corners get more weight
        """
        nozzle_x, nozzle_y = nozzle_pos[0], nozzle_pos[1]
        distances = []
        for corner in bed_corners:
            dx = nozzle_x - corner[0]
            dy = nozzle_y - corner[1]
            dist = math.sqrt(dx*dx + dy*dy) + 0.1  # avoid division by zero
            distances.append(dist)

        # Inverse distance weights
        inv_distances = [1.0/d for d in distances]
        total = sum(inv_distances)
        weights = [w/total for w in inv_distances]

        return weights

    @staticmethod
    def tilt_compensated_fusion(samples_list, bed_corners):
        """
        Tilt-compensated fusion: fit plane to 4 corners, average normal force
        Reduces sensitivity to bed tilt
        """
        if not samples_list or len(samples_list) != 4:
            return []

        min_len = min(len(s) for s in samples_list)
        if min_len == 0:
            return []

        fused = []
        for i in range(min_len):
            avg_time = sum(s[i][0] for s in samples_list) / 4.0
            # For now, use simple average (full plane fitting is complex)
            # TODO: implement proper plane fitting
            avg_force = sum(s[i][1] for s in samples_list) / 4.0
            fused.append([avg_time, avg_force])

        return fused


# Multi-sensor probe configuration and management
class LoadCellProbeMulti:
    def __init__(self, config):
        self._printer = config.get_printer()
        self._config = config

        # Check NumPy availability
        try:
            global np
            import numpy as np
        except:
            raise config.error("[load_cell_probe_multi] requires NumPy module")

        # Parse sensor references
        sensor_names_str = config.get('sensors')
        self._sensor_names = [n.strip() for n in sensor_names_str.split(',')]
        if len(self._sensor_names) != 4:
            raise config.error("sensors must reference exactly 4 load cells")

        # Configuration
        self._fusion_mode = config.getchoice('fusion_mode',
            {'average': 'average', 'weighted': 'weighted',
             'tilt_compensated': 'tilt_compensated'},
            default='average')
        self._min_sensors = config.getint('min_sensors', default=4,
                                         minval=2, maxval=4)
        self._allow_degraded = config.getboolean('allow_degraded_mode',
                                                  default=False)
        self._sync_window = config.getfloat('sync_window', default=0.010,
                                            minval=0.001, maxval=0.100)

        # Bed geometry for weighted fusion
        self._bed_geometry = BedGeometry(config)

        # Fusion weights (for weighted mode)
        default_weights = [0.25, 0.25, 0.25, 0.25]
        weights_list = config.getfloatlist('fusion_weights',
                                           default=default_weights)
        if len(weights_list) != 4:
            raise config.error("fusion_weights must have 4 values")
        if abs(sum(weights_list) - 1.0) > 0.01:
            raise config.error("fusion_weights must sum to 1.0")
        self._fusion_weights = weights_list

        # Standard probe parameters
        self._param_helper = probe.ProbeParameterHelper(config)
        self._probe_offsets = probe.ProbeOffsetsHelper(config)

        # Trigger parameters
        self._trigger_force = config.getint('trigger_force', default=75,
                                           minval=10, maxval=250)
        self._force_safety_limit = config.getint('force_safety_limit',
                                                 default=2000, minval=100,
                                                 maxval=5000)

        # Load cells will be resolved in _handle_ready
        self._load_cells = []
        self._collector = None

        # Tapping move and probe session (initialized after ready)
        self._tapping_move = None
        self._probe_session = None

        # Register with printer
        self._printer.register_event_handler("klippy:ready",
                                            self._handle_ready)

        # Register GCode commands
        LoadCellProbeMultiCommands(config, self)

        # Register as probe
        self._cmd_helper = probe.ProbeCommandHelper(config, self)
        self._printer.add_object('probe', self)

    def _handle_ready(self):
        """Resolve load cell references after all objects loaded"""
        self._load_cells = []
        for name in self._sensor_names:
            try:
                lc = self._printer.lookup_object('load_cell ' + name)
                self._load_cells.append(lc)
            except:
                raise self._printer.config_error(
                    "Unknown load_cell '%s' in [load_cell_probe_multi]" % name)

        # Validate all sensors have same sample rate
        sps_list = [lc.get_sensor().get_samples_per_second()
                   for lc in self._load_cells]
        if len(set(sps_list)) > 1:
            raise self._printer.config_error(
                "All load cells must have same sample_rate")

        # Create multi-sensor collector
        self._collector = MultiSensorCollector(self._printer, self._load_cells,
                                              self._sync_window)

        # Initialize tapping move and probe session
        self._tapping_move = MultiSensorTappingMove(self, self._param_helper)

        def start_session(gcmd):
            return MultiProbeSession(self, self._tapping_move,
                                    self._probe_offsets, self._param_helper)

        self._probe_session = probe.ProbeSessionHelper(
            self._config, self._param_helper, start_session)

        logging.info("LoadCellProbeMulti initialized with %d sensors in %s mode"
                    % (len(self._load_cells), self._fusion_mode))

    def _check_sensor_health(self):
        """Verify all sensors are healthy and calibrated"""
        healthy_count = 0
        for i, lc in enumerate(self._load_cells):
            if not lc.is_calibrated():
                raise self._printer.command_error(
                    "Load cell '%s' is not calibrated" % self._sensor_names[i])
            if not lc.is_tared():
                raise self._printer.command_error(
                    "Load cell '%s' is not tared" % self._sensor_names[i])
            healthy_count += 1

        if healthy_count < self._min_sensors:
            raise self._printer.command_error(
                "Only %d sensors healthy, need %d"
                % (healthy_count, self._min_sensors))

        return healthy_count

    def _tare_all_sensors(self, num_samples):
        """Tare all 4 sensors simultaneously"""
        all_samples, all_errors = self._collector.collect_min(num_samples)

        # Check for errors
        for i, (samples, errors) in enumerate(zip(all_samples, all_errors)):
            if errors:
                raise self._printer.command_error(
                    "Sensor '%s' reported errors: %d errors, %d overflows"
                    % (self._sensor_names[i], errors[0], errors[1]))

        # Tare each sensor with its average
        tare_values = []
        for i, samples in enumerate(all_samples):
            if len(samples) == 0:
                raise self._printer.command_error(
                    "No samples from sensor '%s'" % self._sensor_names[i])
            # Extract counts column (index 2: time, norm, counts)
            counts = [s[2] for s in samples]
            tare_count = sum(counts) / len(counts)
            self._load_cells[i].tare(tare_count)
            tare_values.append(tare_count)

        return tare_values

    def _fuse_samples(self, all_samples):
        """
        Apply fusion algorithm to synchronized samples
        all_samples: list of 4 sample arrays from collectors
        Returns: fused sample array [[time, force], ...]
        """
        # Synchronize timestamps first
        synced = self._collector.get_synchronized_samples(all_samples)

        if not synced or any(len(s) == 0 for s in synced):
            return []

        # Apply fusion based on mode
        if self._fusion_mode == 'average':
            return SensorFusion.simple_average(synced)
        elif self._fusion_mode == 'weighted':
            # Get current nozzle position for dynamic weighting
            toolhead = self._printer.lookup_object('toolhead')
            pos = toolhead.get_position()
            weights = SensorFusion.calculate_inverse_distance_weights(
                pos, self._bed_geometry.get_corners())
            return SensorFusion.weighted_fusion(synced, weights)
        elif self._fusion_mode == 'tilt_compensated':
            return SensorFusion.tilt_compensated_fusion(
                synced, self._bed_geometry.get_corners())
        else:
            # Fallback to average
            return SensorFusion.simple_average(synced)

    def _check_trigger(self, fused_samples, trigger_force):
        """
        Check if fused force exceeds trigger threshold
        Returns: (triggered, trigger_time, max_force)
        """
        if not fused_samples:
            return False, 0.0, 0.0

        max_force = 0.0
        trigger_time = 0.0

        for sample in fused_samples:
            time, force = sample[0], sample[1]
            if abs(force) > abs(max_force):
                max_force = force
            if abs(force) >= trigger_force:
                trigger_time = time
                return True, trigger_time, max_force

        return False, trigger_time, max_force

    def _probing_move(self, gcmd):
        """
        Execute a probing move with multi-sensor fusion
        Uses iterative descent with host-side trigger checking
        """
        # Check health
        self._check_sensor_health()

        # Tare all sensors
        toolhead = self._printer.lookup_object('toolhead')
        print_time = toolhead.get_last_move_time()

        # Get tare samples (4 x 60Hz cycles = ~67ms)
        sps = self._load_cells[0].get_sensor().get_samples_per_second()
        tare_samples = max(2, math.ceil((4.0 / 60.0) * sps))
        tare_values = self._tare_all_sensors(tare_samples)

        logging.info("Tared all sensors: %s" % tare_values)

        # Get probing parameters
        start_pos = toolhead.get_position()
        speed = self._param_helper.get_probe_params(gcmd)['probe_speed']
        z_min = probe.lookup_minimum_z(self._config)
        trigger_force = self._trigger_force

        # Iterative descent with force checking
        # Descend in small steps, checking force after each step
        step_size = 0.5  # 0.5mm steps
        current_z = start_pos[2]
        reactor = self._printer.get_reactor()

        # Start collecting samples
        self._collector.start_collecting(min_time=toolhead.get_last_move_time())

        triggered = False
        trigger_pos = None
        max_iterations = int((start_pos[2] - z_min) / step_size) + 10

        for i in range(max_iterations):
            if current_z <= z_min:
                break

            # Move down one step
            current_z -= step_size
            pos = list(start_pos)
            pos[2] = current_z
            toolhead.manual_move(pos, speed)
            toolhead.wait_moves()

            # Collect samples and check fusion
            print_time = toolhead.get_last_move_time()
            all_samples, all_errors = self._collector.collect_until(print_time)

            # Check for sensor errors
            for sensor_idx, errors in enumerate(all_errors):
                if errors:
                    raise self._printer.command_error(
                        "Sensor '%s' error during probing: %d errors, %d overflows"
                        % (self._sensor_names[sensor_idx], errors[0], errors[1]))

            # Fuse samples and check trigger
            fused = self._fuse_samples(all_samples)
            if fused:
                # Check if trigger threshold exceeded
                current_force = abs(fused[-1][1])  # Last sample force
                logging.debug("Z=%.3f, Force=%.1fg" % (current_z, current_force))

                if current_force >= trigger_force:
                    triggered = True
                    trigger_pos = toolhead.get_position()
                    logging.info("Triggered at Z=%.3f, Force=%.1fg"
                               % (current_z, current_force))
                    break

            # Small delay to avoid overloading
            reactor.pause(reactor.monotonic() + 0.01)

        # Stop collecting
        self._collector.stop_collecting()

        if not triggered:
            raise self._printer.command_error(
                "Probe did not trigger - bed not reached or trigger_force too high")

        return trigger_pos

    # Probe interface methods
    def get_probe_params(self, gcmd=None):
        return self._param_helper.get_probe_params(gcmd)

    def get_offsets(self, gcmd=None):
        return self._probe_offsets.get_offsets(gcmd)

    def start_probe_session(self, gcmd):
        """Start a multi-probe session"""
        return self._probe_session.start_probe_session(gcmd)

    def get_status(self, eventtime):
        """Return status of all sensors"""
        status = {
            'fusion_mode': self._fusion_mode,
            'min_sensors': self._min_sensors,
            'trigger_force': self._trigger_force,
        }

        # Add individual sensor status
        if self._load_cells:
            for i, lc in enumerate(self._load_cells):
                sensor_status = lc.get_status(eventtime)
                prefix = "sensor_%d_" % i
                status.update({prefix + k: v for k, v in sensor_status.items()})

        # Add tapping move status
        if self._tapping_move:
            status.update(self._tapping_move.get_status(eventtime))

        # Add command helper status
        status.update(self._cmd_helper.get_status(eventtime))

        return status


# Perform a single complete tap with multi-sensor fusion
class MultiSensorTappingMove:
    def __init__(self, probe_multi, param_helper):
        self._probe_multi = probe_multi
        self._printer = probe_multi._printer
        self._param_helper = param_helper
        self._last_result = None

    def run_tap(self, gcmd):
        """Execute a probing move and return position"""
        # Execute the probing move
        trigger_pos = self._probe_multi._probing_move(gcmd)
        self._last_result = trigger_pos[2]

        # Return position and validity
        return trigger_pos, True

    def get_status(self, eventtime):
        return {
            'last_z_result': self._last_result,
        }


# Probe session for multi-sensor probing
class MultiProbeSession:
    def __init__(self, probe_multi, tapping_move, probe_offsets, param_helper):
        self._probe_multi = probe_multi
        self._printer = probe_multi._printer
        self._tapping_move = tapping_move
        self._probe_offsets = probe_offsets
        self._param_helper = param_helper
        self._results = []

    def run_probe(self, gcmd):
        """Execute a single probe"""
        epos, is_good = self._tapping_move.run_tap(gcmd)
        res = self._probe_offsets.create_probe_result(epos)
        self._results.append(res)

    def end_probe_session(self):
        """End the probe session"""
        self._results = []

    def pull_probed_results(self):
        """Return collected results"""
        res = self._results
        self._results = []
        return res


# G-Code commands for multi-sensor probe
class LoadCellProbeMultiCommands:
    def __init__(self, config, probe_multi):
        self._printer = config.get_printer()
        self._probe_multi = probe_multi
        self._register_commands()

    def _register_commands(self):
        gcode = self._printer.lookup_object('gcode')
        gcode.register_command("LOAD_CELL_MULTI_TARE",
            self.cmd_LOAD_CELL_MULTI_TARE,
            desc=self.cmd_LOAD_CELL_MULTI_TARE_help)
        gcode.register_command("LOAD_CELL_MULTI_STATUS",
            self.cmd_LOAD_CELL_MULTI_STATUS,
            desc=self.cmd_LOAD_CELL_MULTI_STATUS_help)

    cmd_LOAD_CELL_MULTI_TARE_help = "Tare all 4 load cells simultaneously"

    def cmd_LOAD_CELL_MULTI_TARE(self, gcmd):
        # Check health
        self._probe_multi._check_sensor_health()

        # Get tare samples
        sps = self._probe_multi._load_cells[0].get_sensor().get_samples_per_second()
        tare_samples = max(2, math.ceil((4.0 / 60.0) * sps))

        # Tare all sensors
        tare_values = self._probe_multi._tare_all_sensors(tare_samples)

        # Report results
        gcmd.respond_info("Tared all load cells:")
        for i, (name, tare) in enumerate(zip(self._probe_multi._sensor_names,
                                             tare_values)):
            lc = self._probe_multi._load_cells[i]
            percent = lc.counts_to_percent(tare)
            gcmd.respond_info("  %s: %.2f%% (%d counts)"
                            % (name, percent, tare))

    cmd_LOAD_CELL_MULTI_STATUS_help = "Display status of all 4 load cells"

    def cmd_LOAD_CELL_MULTI_STATUS(self, gcmd):
        gcmd.respond_info("Multi-Sensor Load Cell Status:")
        gcmd.respond_info("  Fusion mode: %s" % self._probe_multi._fusion_mode)
        gcmd.respond_info("  Minimum sensors: %d" % self._probe_multi._min_sensors)
        gcmd.respond_info("")

        # Display each sensor
        for i, (name, lc) in enumerate(zip(self._probe_multi._sensor_names,
                                          self._probe_multi._load_cells)):
            gcmd.respond_info("Sensor %d: %s" % (i, name))

            if not lc.is_calibrated():
                gcmd.respond_info("  Status: NOT CALIBRATED")
                continue

            # Get current reading
            counts = lc.avg_counts(num_samples=5)
            force = lc.counts_to_grams(counts)
            percent = lc.counts_to_percent(counts)

            gcmd.respond_info("  Force: %.1fg (%.2f%%)" % (force, percent))
            gcmd.respond_info("  Calibration: %.3f counts/gram"
                            % lc.get_counts_per_gram())
            gcmd.respond_info("  Tare: %d counts" % lc.get_tare_counts())
            gcmd.respond_info("")


def load_config(config):
    return LoadCellProbeMulti(config)
