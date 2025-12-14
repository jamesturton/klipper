// Main entry point for hifi4
//
// Copyright (C) 2025  James Turton <james.turton@gmx.com>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "sched.h" // sched_main
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#include <hal_log.h>
// #include <hal_timer.h>
#include <hal_gpio.h>
#include <hal_uart.h>

#include "util.h"

/* Define the GPIO pin - PE12 is gpio 140 */
#define LED_PIN     GPIOG(15)   /* PE12 = 128 + 12 = 140 */

/*
 * GPIO toggle task
 * This task runs in a loop toggling the GPIO pin every second
 */
static void gpio_toggle_task(void)
{
    gpio_data_t state = GPIO_DATA_LOW;

    hal_gpio_get_data(LED_PIN, &state);
    
    print("GPIO Toggle Task Started - Toggling PE12 (gpio140) every second\n");
    
    /* Toggle the GPIO state */
    state = (state == GPIO_DATA_LOW) ? GPIO_DATA_HIGH : GPIO_DATA_LOW;
    
    /* Set the GPIO output */
    if (hal_gpio_set_data(LED_PIN, state) == 0) {
        print("GPIO PE12 TOGGLE");
    } else {
        print("Error setting GPIO PE12\n");
    }
}

/*
 * Initialize and start the GPIO toggle example
 */
void gpio_toggle_example_init(void)
{
    int ret;
    
    print("Initializing GPIO toggle example for PE12 (gpio140)\n");
    
    /* Initialize GPIO subsystem */
    ret = hal_gpio_init();
    if (ret != 0) {
        print("Failed to initialize GPIO subsystem\n");
        return;
    }
    
    /* Configure PE12 as output */
    ret = hal_gpio_pinmux_set_function(LED_PIN, GPIO_MUXSEL_OUT);
    if (ret != 0) {
        print("Failed to set PE12 pinmux to output\n");
        return;
    }
    
    ret = hal_gpio_set_direction(LED_PIN, GPIO_DIRECTION_OUTPUT);
    if (ret != 0) {
        print("Failed to set PE12 direction to output\n");
        return;
    }
    
    /* Set initial state to LOW */
    hal_gpio_set_data(LED_PIN, GPIO_DATA_HIGH);
    
    // /* Create the toggle task */
    // if (xTaskCreate(gpio_toggle_task, 
    //                 "GPIO_Toggle",
    //                 configMINIMAL_STACK_SIZE * 2,
    //                 NULL,
    //                 tskIDLE_PRIORITY + 1,
    //                 NULL) != pdPASS) {
    //     print("Failed to create GPIO toggle task\n");
    //     return;
    // }
    
    print("GPIO toggle task created successfully\n");
}

// Main entry point for simulator.
int
main(void)
{
    hw_usleep(200);
    // hal_msleep(200);
    gpio_toggle_example_init();

    sched_main();

    while (1) {
        /* Delay for 1 second */
        hw_usleep(1000);
        // hal_msleep(1000);
        gpio_toggle_task();

        // print("OpenCentauri Klipper for HIFI4 DSP v0.0.0, Build on xtensa-hifi4-elf-gcc \n");
        char tbuf[75] = {"OpenCentauri Klipper for HIFI4 DSP v0.0.0, Build on xtensa-hifi4-elf-gcc \n"};
        hal_uart_send(0, tbuf, 74);
    }

    return 0;
}
