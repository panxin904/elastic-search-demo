---
title: 嵌入式 Rust
---

# 嵌入式 Rust

Rust 嵌入式生态成熟：用 no std 编程微控制器，类型安全 + 零运行时开销 + 强大生态。

## 一句话总结

> **嵌入式 Rust = no_std + 裸机 + 外设访问**。**核心：cortex-m / embedded-hal / RTIC / probe-rs**。

---

## 嵌入式 Rust 工具链

```bash
rustup target add thumbv7em-none-eabihf  # ARM Cortex-M4F
rustup target add riscv32imc-unknown-none-elf  # RISC-V

cargo install probe-rs
cargo install cargo-binutils
```

## Hello LED（STM32）

```rust
#![no_std]
#![no_main]

use panic_halt as _;
use cortex_m_rt::entry;
use stm32f4::stm32f407::{GPIOA, RCC};

#[entry]
fn main() -> ! {
    let peripherals = stm32f407::Peripherals::take().unwrap();
    let rcc = &peripherals.RCC;
    let gpioa = &peripherals.GPIOA;

    rcc.ahb1enr.modify(|_, w| w.gpioaen().set_bit());

    gpioa.moder.modify(|_, w| unsafe { w.bits(0b01 << (5 * 2)) });

    loop {
        gpioa.bsrr.write(|w| unsafe { w.bits(1 << 5) });
        for _ in 0..1_000_000 { cortex_m::asm::nop(); }
        gpioa.bsrr.write(|w| unsafe { w.bits(1 << (5 + 16)) });
        for _ in 0..1_000_000 { cortex_m::asm::nop(); }
    }
}
```

## embedded-hal：硬件抽象

```rust
use embedded_hal::digital::v2::OutputPin;

struct Led<P: OutputPin> {
    pin: P,
}

impl<P: OutputPin> Led<P> {
    fn new(pin: P) -> Self {
        Self { pin }
    }

    fn on(&mut self) -> Result<(), P::Error> {
        self.pin.set_high()
    }

    fn off(&mut self) -> Result<(), P::Error> {
        self.pin.set_low()
    }
}
```

## RTIC：实时中断驱动并发

```toml
[dependencies]
rtic = "1.0"
```

```rust
#![no_std]
#![no_main]

use rtic::app;
use panic_halt as _;

#[app(device = stm32f4::stm32f407, peripherals = true)]
const APP: () = {
    struct Resources {
        led: gpioa::PA5<Output<PushPull>>,
    }

    #[init]
    fn init(cx: init::Context) -> init::LateResources {
        let dp = cx.device;
        let gpioa = dp.GPIOA.split();
        let led = gpioa.pa5.into_push_pull_output();

        init::LateResources { led }
    }

    #[task(binds = TIM2, resources = [led])]
    fn toggle(cx: toggle::Context) {
        cx.resources.led.toggle().unwrap();
    }

    #[idle]
    fn idle(_cx: idle::Context) -> ! {
        loop {
            cortex_m::asm::wfi();
        }
    }
};
```

## Embassy：现代异步嵌入式

```toml
[dependencies]
embassy-stm32 = "0.1"
embassy-executor = "0.3"
```

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};
use embassy_stm32::gpio::{Output, Level, Speed};
use panic_halt as _;

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    let p = embassy_stm32::init(Default::default());
    let mut led = Output::new(p.PA5, Level::High, Speed::Low);

    loop {
        led.set_high();
        Timer::after(Duration::from_millis(500)).await;
        led.set_low();
        Timer::after(Duration::from_millis(500)).await;
    }
}
```

## probe-rs：烧录 + 调试

```bash
cargo run --release
probe-rs debug --chip STM32F407VGTx
probe-rs run --chip STM32F407VGTx
```

## 实战案例：传感器数据采集

```rust
use embedded_hal::blocking::i2c::{Write, Read};

struct Bme280<I2C> {
    i2c: I2C,
    address: u8,
}

impl<I2C> Bme280<I2C>
where
    I2C: Write + Read,
{
    fn new(i2c: I2C) -> Self {
        Self { i2c, address: 0x76 }
    }

    fn read_temperature(&mut self) -> Result<f32, I2C::Error> {
        self.i2c.write(self.address, &[0xF4, 0x27])?;

        let mut buf = [0u8; 3];
        self.i2c.write(self.address, &[0xF8])?;
        self.i2c.read(self.address, &mut buf)?;

        let raw = ((buf[0] as u32) << 12) | ((buf[1] as u32) << 4) | ((buf[2] as u32) >> 4);
        Ok((raw as f32) / 5120.0)
    }
}
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/ffi**：FFI
- **05-systems/unsafe**：unsafe Rust

## 一句话总结

> **嵌入式 Rust = no_std + HAL 抽象 + RTIC/Embassy**。**类型安全 + 零开销，让嵌入式更可靠**。
