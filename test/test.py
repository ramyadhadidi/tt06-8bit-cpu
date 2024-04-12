# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: MIT

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_obvious(dut):
    assert 2 > 1, "Testing the obvious"

@cocotb.test()
async def test_load_bytes_and_check_internal_signal(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for a few clock cycles after reset

    # Setup LDB (Load Byte) test conditions
    test_value = 123
    register_address = 3
    dut.ui_in.value = int(f'0001{register_address:04b}', 2)  # Format LDB command
    dut.uio_in.value = test_value
    await RisingEdge(dut.clk)  # Execute LDB command

    # Ensure data has been written and propagated through the design
    await ClockCycles(dut.clk, 1)

    # Verify internal state after LDB operation
    # Verifying written data matches input
    internal_value = int(dut.myCPU.w_data.value)
    assert internal_value == test_value, f"Data mismatch: expected {test_value}, found {internal_value}"

    # Verifying write signal is active
    internal_value = int(dut.myCPU.write.value)
    assert internal_value == 1, "Write signal not active as expected"

    # Verifying the target register address
    internal_value = int(dut.myCPU.w_reg.value)
    assert internal_value == register_address, f"Register address mismatch: expected {register_address}, found {internal_value}"

    # Verifying reg_file write signal
    internal_value = int(dut.myCPU.RF1.write.value)
    assert internal_value == 1, "reg_file write signal not active as expected"

    # Verifying reg_file target register address
    internal_value = int(dut.myCPU.RF1.w_reg.value)
    assert internal_value == register_address, f"reg_file register address mismatch: expected {register_address}, found {internal_value}"

    # Verifying reg_file written data
    internal_value = int(dut.myCPU.RF1.w_d.value)
    assert internal_value == test_value, f"reg_file data mismatch: expected {test_value}, found {internal_value}"

    # Verifying the actual register content
    internal_value = int(dut.myCPU.RF1.reg_data[register_address].value)
    assert internal_value == test_value, f"Register content mismatch: expected {test_value}, found {internal_value}"

    cocotb.log.info("LDB operation successfully verified across all relevant internal signals.")


@cocotb.test()
async def test_load_and_store_bytes(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for a few clock cycles after reset

    # Load Byte (LDB) - Setup
    test_value = 123
    register_address = 3
    dut.ui_in.value = int(f'0001{register_address:04b}', 2)  # Format LDB command
    dut.uio_in.value = test_value
    await RisingEdge(dut.clk)  # Execute LDB command
    await ClockCycles(dut.clk, 1)  # Ensure the write operation completes

    # Store Byte (STB) - Setup
    dut.ui_in.value = int(f'0010{register_address:04b}', 2)  # Format STB command; reuse register_address
    await RisingEdge(dut.clk)  # Execute STB command

    # The output should now be the test value if the STB command outputs to `uo_out`
    await RisingEdge(dut.clk)  # Wait one clock cycle for data to propagate if needed
    output_value = int(dut.uo_out.value)  # Read the output port that should receive the stored value

    assert output_value == test_value, f"STB test failed: expected {test_value} at output, found {output_value}"

    # Optionally verify internal flags or additional outputs if the architecture specifies them
    # For example, checking if a write-back to memory or another output was performed correctly

    cocotb.log.info("LDB and STB operations successfully verified.")


# @cocotb.test()
# async def test_project(dut):
#   dut._log.info("Start")

#   clock = Clock(dut.clk, 10, units="us")
#   cocotb.start_soon(clock.start())

#   # Reset
#   dut._log.info("Reset")
#   dut.ena.value = 1
#   dut.ui_in.value = 0
#   dut.uio_in.value = 0
#   dut.rst_n.value = 0
#   await ClockCycles(dut.clk, 10)
#   dut.rst_n.value = 1

#   # Set the input values, wait one clock cycle, and check the output
#   dut._log.info("Test")
#   dut.ui_in.value = 20
#   dut.uio_in.value = 30

#   await ClockCycles(dut.clk, 10)

#   assert dut.uo_out.value == 50
