#include "portmacro.h"
#include "projdefs.h"

extern void _xt_tick_divisor_init(void);
BaseType_t xTaskIncrementTick( void ) PRIVILEGED_FUNCTION;

/*
 * Defines the memory ranges allocated to the task when an MPU is used.
 */
typedef struct xMEMORY_REGION
{
	void *pvBaseAddress;
	uint32_t ulLengthInBytes;
	uint32_t ulParameters;
} MemoryRegion_t;
