// GPIO functions on hifi4.
//
// Copyright (C) 2025  James Turton <james.turton@gmx.com>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "gpio.h" // gpio_out_write

struct gpio_out gpio_out_setup(uint8_t pin, uint8_t val) {
    hal_gpio_init();
    struct gpio_out g = { .pin=(gpio_data_t)pin };
    gpio_out_reset(g, val);
    return g;
}
void gpio_out_reset(struct gpio_out g, uint8_t val) {
    hal_gpio_pinmux_set_function(g.pin, GPIO_MUXSEL_OUT);
    hal_gpio_set_direction(g.pin, GPIO_DIRECTION_OUTPUT);
    hal_gpio_set_data(g.pin, val ? GPIO_DATA_HIGH : GPIO_DATA_LOW);
}
void gpio_out_toggle_noirq(struct gpio_out g) {
    gpio_data_t state;
    hal_gpio_get_data(g.pin, &state);
    state = (state == GPIO_DATA_LOW) ? GPIO_DATA_HIGH : GPIO_DATA_LOW;
    hal_gpio_set_data(g.pin, state);
}
void gpio_out_toggle(struct gpio_out g) {
    gpio_out_toggle_noirq(g);
}
void gpio_out_write(struct gpio_out g, uint8_t val) {
    gpio_data_t state = val ? GPIO_DATA_HIGH : GPIO_DATA_LOW;
    hal_gpio_set_data(g.pin, state);
}
struct gpio_in gpio_in_setup(uint8_t pin, int8_t pull_up) {
    hal_gpio_init();
    struct gpio_in g = { .pin=(gpio_data_t)pin };
    gpio_in_reset(g, pull_up);
    return g;
}
void gpio_in_reset(struct gpio_in g, int8_t pull_up) {
    hal_gpio_pinmux_set_function(g.pin, GPIO_MUXSEL_IN);
    hal_gpio_set_direction(g.pin, GPIO_DIRECTION_INPUT);
    hal_gpio_set_pull(g.pin, pull_up ? GPIO_PULL_UP : GPIO_PULL_DOWN_DISABLED);
}
uint8_t gpio_in_read(struct gpio_in g) {
    gpio_data_t state;
    hal_gpio_get_data(g.pin, &state);
    return state;
}
struct gpio_pwm gpio_pwm_setup(uint8_t pin, uint32_t cycle_time, uint8_t val) {
    return (struct gpio_pwm){.pin=pin};
}
void gpio_pwm_write(struct gpio_pwm g, uint8_t val) {
}
struct gpio_adc gpio_adc_setup(uint8_t pin) {
    return (struct gpio_adc){.pin=pin};
}
uint32_t gpio_adc_sample(struct gpio_adc g) {
    return 0;
}
uint16_t gpio_adc_read(struct gpio_adc g) {
    return 0;
}
void gpio_adc_cancel_sample(struct gpio_adc g) {
}

struct spi_config
spi_setup(uint32_t bus, uint8_t mode, uint32_t rate)
{
    return (struct spi_config){ };
}
void
spi_prepare(struct spi_config config)
{
}
void
spi_transfer(struct spi_config config, uint8_t receive_data
             , uint8_t len, uint8_t *data)
{
}
