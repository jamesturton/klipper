# Additional HIFI4 build rules

# Setup the toolchain
CROSS_PREFIX=xtensa-nxp_rt700_hifi4_zephyr-elf-

dirs-y += src/generic
dirs-y += src/hifi4
dirs-y += lib/hifi4
dirs-y += lib/hifi4/portable
dirs-y += lib/hifi4/rtos-hal
dirs-y += lib/hifi4/rtos-hal/source
dirs-y += lib/hifi4/rtos-hal/source/hal/gpio/sun8iw20
dirs-y += lib/hifi4/rtos-hal/source/hal/uart
dirs-y += lib/hifi4/rtos-hal/source/hal/timer
dirs-y += lib/hifi4/rtos-hal/source/hal/ccmu/sunxi-ng
dirs-y += lib/hifi4/rtos-hal/source/osal

# RTOS HAL configuration
CFLAGS += -DCONFIG_KERNEL_FREERTOS
CFLAGS += -DCONFIG_CORE_DSP0
CFLAGS += -DCONFIG_ARCH_SUN8IW20
CFLAGS += -DCONFIG_LOG_LEVEL=0
CFLAGS += -DCONFIG_DRIVERS_SUNXI_CCU

CFLAGS += -O2 -mlongcalls -mtext-section-literals -mabi=call0

# rtos-hal
CFLAGS += -I lib/hifi4
CFLAGS += -I lib/hifi4/rtos-hal/include
CFLAGS += -I lib/hifi4/rtos-hal/include/hal
CFLAGS += -I lib/hifi4/rtos-hal/include/osal
CFLAGS += -I lib/hifi4/rtos-hal/include/xtensa
CFLAGS += -I lib/hifi4/rtos-hal/source/hal

CFLAGS += -I lib/hifi4/portable

CFLAGS_klipper.elf += -Wl,--script src/hifi4/hifi4.ld
CFLAGS_klipper.elf += -nostdlib
CFLAGS_klipper.elf += -Wl,--gc-sections
CFLAGS_klipper.elf += -Wl,--abi-call0
CFLAGS_klipper.elf += -Wl,-Map,$(OUT)/dsp.map

ASFLAGS += -Wa,--abi-call0
ASFLAGS += -Ilib/hifi4
ASFLAGS += -Ilib/hifi4/rtos-hal/include
ASFLAGS += -Ilib/hifi4/portable

# Add source files
src-y += hifi4/main.c
src-y += hifi4/util.c 
src-y += hifi4/gpio.c
src-y += hifi4/irq.c
src-y += hifi4/timer.c
src-y += hifi4/serial.c
src-y += ../lib/hifi4/portable/port.c

# rtos-hal
src-y += ../lib/hifi4/rtos-hal/source/hal/gpio/hal_gpio.c
src-y += ../lib/hifi4/rtos-hal/source/hal/gpio/sun8iw20/gpio-sun8iw20.c
src-y += ../lib/hifi4/rtos-hal/source/hal/timer/hal_timer.c
src-y += ../lib/hifi4/rtos-hal/source/hal/timer/sunxi_timer.c
src-y += ../lib/hifi4/rtos-hal/source/hal/uart/hal_uart.c
src-y += ../lib/hifi4/rtos-hal/source/hal/ccmu/hal_reset.c
src-y += ../lib/hifi4/rtos-hal/source/hal/ccmu/hal_clk.c
src-y += ../lib/hifi4/rtos-hal/source/hal/ccmu/sunxi-ng/ccu.c
src-y += ../lib/hifi4/rtos-hal/source/hal/ccmu/sunxi-ng/clk.c

# osal
src-y += ../lib/hifi4/rtos-hal/source/osal/hal_mem.c
src-y += ../lib/hifi4/rtos-hal/source/osal/hal_interrupt.c

# generic
src-y += generic/timer_irq.c
src-y += generic/crc16_ccitt.c
src-y += generic/alloc.c
src-y += generic/serial_irq.c

OBJS_klipper.elf += $(OUT)lib/hifi4/crt1.o
OBJS_klipper.elf += $(OUT)lib/hifi4/oemhead.o
OBJS_klipper.elf += $(OUT)lib/hifi4/intlevel-set.o
OBJS_klipper.elf += $(OUT)lib/hifi4/setjmp.o

$(OUT)%.o: %.S
	@echo "  Compiling $@"
	$(Q)$(CC) $(ASFLAGS) -c $(PWD)/$< -o $@
