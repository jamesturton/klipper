// Timer functions for hifi4.
//
// Copyright (C) 2025  James Turton <james.turton@gmx.com>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "timer.h"
#include "compiler.h"
#include <sunxi_hal_timer.h>
#include <timer/sunxi_timer.h>
#include "board/irq.h" // irq_disable
#include "board/misc.h" // timer_read_time
#include "board/timer_irq.h" // timer_dispatch_many
#include "sched.h" // DECL_INIT

static uint32_t timer1_total_times;

/****************************************************************
 * Low level timer code
 ****************************************************************/

// Hardware timer IRQ handler - dispatch software timers
void __visible __aligned(16)
TIMER0_IRQHandler(void *)
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
    // timer is a count down timer so we have to invert the value
    uint32_t ret = hal_readl(TIMER_CNTVAL_REG(SUNXI_TMR1));
    ret = 0xffffffff - ret;
    return ret;
}

inline void
timer_set(uint32_t next)
{
    hal_timer_set_periodic(next, SUNXI_TMR0, TIMER0_IRQHandler, NULL);
}

// Activate timer dispatch as soon as possible
void
timer_kick(void)
{
    timer_set(1);
}

// Dummy timer to avoid scheduling a SysTick irq greater than 0xffffff
static uint_fast8_t
timer_wrap_event(struct timer *t)
{
    t->waketime += 0xffffff;
    return SF_RESCHEDULE;
}
static struct timer wrap_timer = {
    .func = timer_wrap_event,
    .waketime = 0xffffff,
};

void timer_reset(void)
{
    if (timer_from_us(100000) <= 0xffffff)  //100ms Timer in sched.c already ensures SysTick wont overflow
        return;

    sched_add_timer(&wrap_timer);
}
DECL_SHUTDOWN(timer_reset);

/****************************************************************
 * Setup and irqs
 ****************************************************************/
static void TIMER1_IRQHandler(void *param)
{
   timer1_total_times += 1;
}

void
timer_init(void)
{
    timer1_total_times = 0;
    irqstatus_t flag = irq_save();

    hal_timer_init(SUNXI_TMR1);
    hal_timer_set_periodic(0xffffffff, SUNXI_TMR1, TIMER1_IRQHandler, NULL);//0xffffffff 20000000
    timer_reset();

    hal_timer_init(SUNXI_TMR0);
    hal_timer_set_periodic(200000, SUNXI_TMR0, TIMER0_IRQHandler, NULL);
    timer_kick();
    irq_restore(flag);
}
DECL_INIT(timer_init);
