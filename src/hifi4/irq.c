// Interrupt functions on hifi4.
//
// Copyright (C) 2025  James Turton <james.turton@gmx.com>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include <hal_interrupt.h>
#include "generic/irq.h" // irqstatus_t

// Disable hardware interrupts
void
irq_disable(void)
{
    hal_interrupt_disable();
}

// Enable hardware interrupts
void
irq_enable(void)
{
    hal_interrupt_enable();
}

// Disable hardware interrupts in not already disabled
irqstatus_t
irq_save(void)
{
    return hal_interrupt_save();
}

// Restore hardware interrupts to state from flag returned by irq_save()
void irq_restore(irqstatus_t flag)
{
    hal_interrupt_restore(flag);
}

// Atomically enable hardware interrupts and sleep processor until next irq
void irq_wait(void)
{
    hal_interrupt_enable();
    asm("nop\n    nop\n    nop" : : : "memory");
    hal_interrupt_disable();
}

// Check if an interrupt is active (used only on architectures that do
// not have hardware interrupts)
void irq_poll(void)
{
}
