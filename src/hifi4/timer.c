// Example code for running timers in a polling mode
//
// Copyright (C) 2018  Kevin O'Connor <kevin@koconnor.net>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include <sunxi_hal_timer.h>
#include "board/irq.h" // irq_disable
#include "board/misc.h" // timer_read_time
#include "board/timer_irq.h" // timer_dispatch_many
#include "sched.h" // DECL_INIT

/****************************************************************
 * Low level timer code
 ****************************************************************/

// Hardware timer IRQ handler - dispatch software timers
void // __aligned(16)
TIMER0_IRQHandler(void)
{
    irq_disable();
    uint32_t next = timer_dispatch_many();
    timer_set(next);
    irq_enable();
}

// Return the current time (in absolute clock ticks).
uint32_t
timer_read_time(void)
{
    return 0;
}

inline void
timer_set(uint32_t next)
{
    hal_timer_set_oneshot(SUNXI_TMR0, next, TIMER0_IRQHandler, NULL);
}

// Activate timer dispatch as soon as possible
void
timer_kick(void)
{
    hal_timer_set_oneshot(SUNXI_TMR0, 50, TIMER0_IRQHandler, NULL);
}

/****************************************************************
 * Setup and irqs
 ****************************************************************/

void
timer_init(void)
{
    hal_timer_init(SUNXI_TMR0);
}
DECL_INIT(timer_init);
