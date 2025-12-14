# Additional HIFI4 build rules

# Setup the toolchain
CROSS_PREFIX=xtensa-hifi4-elf-

# dirs-y += src/generic
dirs-y += src/hifi4
dirs-y += lib/hifi4
dirs-y += lib/hifi4/rtos-hal
dirs-y += lib/hifi4/rtos-hal/source
dirs-y += lib/hifi4/rtos-hal/source/hal/gpio/sun8iw20
dirs-y += lib/hifi4/rtos-hal/source/hal/uart
dirs-y += lib/hifi4/rtos-hal/source/hal/timer
dirs-y += lib/hifi4/rtos-hal/source/osal

# CFLAGS := -iquote $(OUT) -iquote src -iquote $(OUT)board-generic/ -DXT_BOARD  -DXT_TIMER_INDEX=0 -DXT_USE_SWPRI -DSTANDALONE=1 
# CFLAGS += -DXTUTIL_NO_OVERRIDE 

# RTOS HAL configuration
CFLAGS += -DCONFIG_KERNEL_FREERTOS
CFLAGS += -DCONFIG_CORE_DSP0
CFLAGS += -DCONFIG_ARCH_SUN8IW20
CFLAGS += -DCONFIG_LOG_LEVEL=0
CFLAGS += -DCONFIG_DRIVERS_SUNXI_CCU

# CFLAGS += -Wa,--longcalls -static -O2  -Wall -mtext-section-literals  -fno-inline-functions
# CFLAGS += -ffunction-sections -fdata-sections  -mlongcalls  $(DFLAGS) $(IFLAGS)
# CFLAGS += -std=c99 -Wextra -Wa,--no-generate-flix -mtarget-align 
# CFLAGS += -Wno-unused-variable -Wno-unused-function

CFLAGS += -O2 -mlongcalls -mtext-section-literals -mabi=call0

# rtos-hal
CFLAGS += -I lib/hifi4
CFLAGS += -I lib/hifi4/rtos-hal/include
CFLAGS += -I lib/hifi4/rtos-hal/include/hal
CFLAGS += -I lib/hifi4/rtos-hal/include/osal
CFLAGS += -I lib/hifi4/rtos-hal/include/xtensa
CFLAGS += -I lib/hifi4/rtos-hal/source/hal

CFLAGS += -I lib/hifi4/portable

CFLAGS_klipper.elf += -Wl,--script src/hifi4/hifi4.ld -nostdlib
# CFLAGS_klipper.elf += -nostdlib -Wl,--gc-sections -Wl,--defsym=__prefctl_default=0x144 
# CFLAGS_klipper.elf += -Wl,--defsym=__memctl_default_post=1
# CFLAGS_klipper.elf += -Wl,--abi-windowed
# CFLAGS_klipper.elf += -Wl,--no-windowed
# CFLAGS_klipper.elf += -Wl,-Map,$(OUT)/dsp.map

ASFLAGS += --abi-call0
ASFLAGS += -Ilib/hifi4
# ASFLAGS += -Ilib/hifi4/portable
# ASFLAGS += -Ilib/hifi4/oemhead

# LIBS = -L lib/hifi4/lib/ -lxtutil  -lhandler-reset -lc -lgloss -lhal -lm -lgcc -lc

# LIB_OBJS := lib/hifi4/lib/crti.o
# LIB_OBJS += lib/hifi4/lib/crtbegin.o
# LIB_OBJS += lib/hifi4/lib/crtend.o
# LIB_OBJS += lib/hifi4/lib/crtn.o

# CFLAGS_klipper.elf += $(LIB_OBJS) $(LIBS)

# Add source files
src-y += hifi4/main.c hifi4/util.c hifi4/gpio.c # hifi4/timer.c hifi4/serial.c
# src-y += ../lib/hifi4/board-init.c

# rtos-hal
# src-y += ../lib/hifi4/rtos-hal/source/hal/common/dma_alloc.c
src-y += ../lib/hifi4/rtos-hal/source/hal/gpio/hal_gpio.c
src-y += ../lib/hifi4/rtos-hal/source/hal/gpio/sun8iw20/gpio-sun8iw20.c
# src-y += ../lib/hifi4/rtos-hal/source/hal/timer/hal_timer.c
src-y += ../lib/hifi4/rtos-hal/source/hal/uart/hal_uart.c

# OSAL (Operating System Abstraction Layer) sources
src-y += ../lib/hifi4/rtos-hal/source/osal/hal_mem.c
src-y += ../lib/hifi4/rtos-hal/source/osal/hal_interrupt.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_atomic.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_cache.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_sem.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_mutex.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_queue.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_timer.c
# src-y += ../lib/hifi4/rtos-hal/source/osal/hal_thread.c

#generic
# src-y += generic/crc16_ccitt.c generic/alloc.c
# src-y += generic/timer_irq.c generic/serial_irq.c

OBJS_klipper.elf += $(OUT)lib/hifi4/crt1.o
OBJS_klipper.elf += $(OUT)lib/hifi4/oemhead.o

$(OUT)%.o: %.S
	@echo "  Compiling $@"
	$(Q)$(AS) $(ASFLAGS) -c $(PWD)/$< -o $@
