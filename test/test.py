# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: MIT

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_obvious(dut):
    assert 2 > 1, "Testing the obvious"

'''
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
    test_value = 254
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

@cocotb.test()
async def test_alu_xor_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for a few clock cycles after reset

    # Load Byte into Register 1
    value1 = 0xAA
    register1 = 1
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)

    # Load Byte into Register 2
    value2 = 0x55
    register2 = 2
    dut.ui_in.value = int(f'0001{register2:04b}', 2)  # LDB command for Register 2
    dut.uio_in.value = value2
    await RisingEdge(dut.clk)

    # Execute XOR Operation on Register 1 and Register 2
    register3 = 3  # Result register
    dut.ui_in.value = int(f'1101{register3:04b}', 2)  # XOR command
    dut.uio_in.value = int(f'{register2:04b}{register1:04b}', 2)  # r2 and r1; result in r3
    await RisingEdge(dut.clk)

    # Check internal values after XOR operation
    assert int(dut.myCPU.inst.value) == int('1101', 2), "Instruction mismatch in XOR operation."
    assert int(dut.myCPU.r_reg1.value) == register2, "Source register 1 address mismatch."
    assert int(dut.myCPU.r_reg2.value) == register1, "Source register 2 address mismatch."
    assert int(dut.myCPU.w_reg.value) == register3, "Target register for result mismatch."
    assert int(dut.myCPU.alu_op.value) == 5, "ALU operation code mismatch for XOR."
    assert int(dut.myCPU.alu_in1.value) == value2, "First input to ALU mismatch."
    assert int(dut.myCPU.alu_in2.value) == value1, "Second input to ALU mismatch."
    assert int(dut.myCPU.alu_out.value) == (value1 ^ value2), "ALU output mismatch for XOR operation."
    assert int(dut.myCPU.w_data.value) == (value1 ^ value2), "Data to be written back mismatch."

    await ClockCycles(dut.clk, 1)

    assert int(dut.myCPU.RF1.reg_data[register3].value) == (value1 ^ value2), "Final result in register mismatch."

    # Verify the output after storing the result
    dut.ui_in.value = int(f'0010{register3:04b}', 2)  # STB command to output the result

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    output_value = int(dut.uo_out.value)
    assert output_value == (value1 ^ value2), f"STB output failed: expected {value1 ^ value2}, found {output_value}"

    cocotb.log.info("ALU XOR operation and store test passed successfully.")


@cocotb.test()
async def test_alu_xor_operation_same_register_write(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 0xAA
    register1 = 1
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Load Byte into Register 2
    value2 = 0x55
    register2 = 2
    dut.ui_in.value = int(f'0001{register2:04b}', 2)  # LDB command for Register 2
    dut.uio_in.value = value2
    await RisingEdge(dut.clk)  # Load value into Register 2

    # Execute XOR Operation between Register 1 and Register 2, store in Register 2
    register3 = 2  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1101{register3:04b}', 2)  # XOR command
    dut.uio_in.value = int(f'{register2:04b}{register1:04b}', 2)  # Set operands for XOR
    await RisingEdge(dut.clk)  # Perform XOR operation

    # Check all internal values for consistency and correctness
    assert int(dut.myCPU.inst.value) == int('1101', 2), "Mismatch in expected XOR instruction."
    assert int(dut.myCPU.w_reg.value) == register3, "Incorrect target register for XOR result."
    assert int(dut.myCPU.r_reg1.value) == register2, "Mismatch in first operand register of XOR."
    assert int(dut.myCPU.r_reg2.value) == register1, "Mismatch in second operand register of XOR."
    assert int(dut.myCPU.alu_op.value) == 5, "Incorrect ALU opcode for XOR operation."
    assert int(dut.myCPU.alu_in1.value) == value2, "First input to ALU does not match expected."
    assert int(dut.myCPU.alu_in2.value) == value1, "Second input to ALU does not match expected."
    assert int(dut.myCPU.alu_out.value) == (value1 ^ value2), "ALU output incorrect for XOR operation."
    assert int(dut.myCPU.w_data.value) == (value1 ^ value2), "Data to be written back does not match XOR output."

    await ClockCycles(dut.clk, 1)

    assert int(dut.myCPU.RF1.reg_data[register3].value) == (value1 ^ value2), "Result not correctly written to target register."

    await ClockCycles(dut.clk, 1)

    # Perform STB command to output the result
    dut.ui_in.value = int(f'0010{register3:04b}', 2)  # STB command to output the result

    await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 1)  # Allow output to stabilize

    output_value = int(dut.uo_out.value)
    assert output_value == (value1 ^ value2), f"Output after STB does not match expected value, found {output_value}."

    cocotb.log.info("ALU XOR operation and verification completed successfully.")

@cocotb.test()
async def test_alu_and_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 0xAA
    register1 = 1
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Load Byte into Register 2
    value2 = 0x55
    register2 = 2
    dut.ui_in.value = int(f'0001{register2:04b}', 2)  # LDB command for Register 2
    dut.uio_in.value = value2
    await RisingEdge(dut.clk)  # Load value into Register 2

    # Execute AND Operation between Register 1 and Register 2, store in Register 2
    register3 = 6  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1001{register3:04b}', 2)  # XOR command
    dut.uio_in.value = int(f'{register2:04b}{register1:04b}', 2)  # Set operands for XOR
    await RisingEdge(dut.clk)  # Perform XOR operation

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = value1 & value2
    assert internal_result == expected_result, f"AND test failed: expected {expected_result}, found {internal_result}"

    cocotb.log.info("Simplified ALU AND operation test passed successfully.")


@cocotb.test()
async def test_alu_ora_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 0xAA
    register1 = 3
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Load Byte into Register 2
    value2 = 0x55
    register2 = 8
    dut.ui_in.value = int(f'0001{register2:04b}', 2)  # LDB command for Register 2
    dut.uio_in.value = value2
    await RisingEdge(dut.clk)  # Load value into Register 2

    # Execute ORA Operation between Register 1 and Register 2, store in Register 2
    register3 = 6  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1010{register3:04b}', 2)  # XOR command
    dut.uio_in.value = int(f'{register2:04b}{register1:04b}', 2)  # Set operands for XOR
    await RisingEdge(dut.clk)  # Perform XOR operation

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = value1 & value2
    assert internal_result == expected_result, f"ORA test failed: expected {expected_result}, found {internal_result}"

    cocotb.log.info("Simplified ALU ORA operation test passed successfully.")

@cocotb.test()
async def test_alu_inc_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 254
    register1 = 3
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Execute INC Operation between Register 1 and Register 2, store in Register 2
    register3 = 3  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1110{register3:04b}', 2)  # XOR command
    dut.uio_in.value = int(f'{register1:04b}0000', 2)  # Set operands for XOR
    await RisingEdge(dut.clk)  # Perform XOR operation

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = value1 + 1
    assert internal_result == expected_result, f"INC test failed: expected {expected_result}, found {internal_result}"

    cocotb.log.info("Simplified ALU INC operation test passed successfully.")

@cocotb.test()
async def test_alu_inc_with_c_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 255
    register1 = 3
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Execute INC Operation between Register 1 and Register 2, store in Register 2
    register3 = 3  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1110{register3:04b}', 2)  # INC command
    dut.uio_in.value = int(f'{register1:04b}0000', 2)  # Set operands for INC
    await RisingEdge(dut.clk)  # Perform INC operation

    assert int(dut.myCPU.ALU1.c.value) == 1
    assert int(dut.myCPU.mux_new_processor_stat.value) == 1
    assert int(dut.myCPU.alu_c.value) == 1
    assert int(dut.myCPU.processor_stat.value) == 0
    assert int(dut.myCPU.rst.value) == 0

    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate

    assert int(dut.myCPU.processor_stat.value) == 1

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = 1
    assert internal_result == expected_result, f"INC test failed: expected {expected_result}, found {internal_result}"

    cocotb.log.info("Simplified INC XOR operation test passed successfully.")

@cocotb.test()
async def test_alu_inc_with_c_operation_with_rds(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 255
    register1 = 3
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Execute INC Operation between Register 1 and Register 2, store in Register 2
    register3 = 3  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1110{register3:04b}', 2)  # INC command
    dut.uio_in.value = int(f'{register1:04b}0000', 2)  # Set operands for INC
    await RisingEdge(dut.clk)  # Perform INC operation

    assert int(dut.myCPU.ALU1.c.value) == 1
    assert int(dut.myCPU.mux_new_processor_stat.value) == 1
    assert int(dut.myCPU.alu_c.value) == 1
    assert int(dut.myCPU.processor_stat.value) == 0
    assert int(dut.myCPU.rst.value) == 0


    dut.ui_in.value = int(f'00110000', 2)  # Format RDS command; reuse register_address
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate

    assert int(dut.myCPU.inst.value) == int('0011', 2)
    assert int(dut.myCPU.mux_processor_stat_data_out.value) == 1
    assert int(dut.myCPU.mux_new_processor_stat.value) == 0
    assert int(dut.myCPU.alu_c.value) == 0
    assert int(dut.myCPU.processor_stat.value) == 1

    assert int(dut.myCPU.processor_stat.value) == 1
    assert int(dut.myCPU.mux_new_processor_stat.value) == 0

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = 0
    assert internal_result == expected_result, f"INC test failed: expected {expected_result}, found {internal_result}"

    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate

    output_value = int(dut.uo_out.value)  # Read the output port that should receive the stored value
    assert output_value == 1, f"RDS test failed: expected 1 at output, found {output_value}"

    cocotb.log.info("Simplified INC RDS operation test passed successfully.")

@cocotb.test()
async def test_alu_add_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 123
    register1 = 3
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Load Byte into Register 2
    value2 = 42
    register2 = 8
    dut.ui_in.value = int(f'0001{register2:04b}', 2)  # LDB command for Register 2
    dut.uio_in.value = value2
    await RisingEdge(dut.clk)  # Load value into Register 2

    # Execute ORA Operation between Register 1 and Register 2, store in Register 2
    register3 = 6  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1011{register3:04b}', 2)  # ADD command
    dut.uio_in.value = int(f'{register2:04b}{register1:04b}', 2)  # Set operands for XOR
    await RisingEdge(dut.clk)  # Perform XOR operation

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = value1 + value2
    assert internal_result == expected_result, f"ORA test failed: expected {expected_result}, found {internal_result}"

    cocotb.log.info("Simplified ALU ADD operation test passed successfully.")


@cocotb.test()
async def test_alu_sub_operation(dut):
    # Initialize the clock to 100 MHz
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    # Reset the device
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)  # Hold reset for 5 clock cycles
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)  # Wait for stability post-reset

    # Load Byte into Register 1
    value1 = 42
    register1 = 3
    dut.ui_in.value = int(f'0001{register1:04b}', 2)  # LDB command for Register 1
    dut.uio_in.value = value1
    await RisingEdge(dut.clk)  # Load value into Register 1

    # Load Byte into Register 2
    value2 = 123
    register2 = 8
    dut.ui_in.value = int(f'0001{register2:04b}', 2)  # LDB command for Register 2
    dut.uio_in.value = value2
    await RisingEdge(dut.clk)  # Load value into Register 2

    # Execute ORA Operation between Register 1 and Register 2, store in Register 2
    register3 = 6  # Overwrite Register 2 with result
    dut.ui_in.value = int(f'1100{register3:04b}', 2)  # SUB command
    dut.uio_in.value = int(f'{register2:04b}{register1:04b}', 2)  # Set operands for XOR
    await RisingEdge(dut.clk)  # Perform XOR operation

    # Verify the output directly
    await ClockCycles(dut.clk, 1)  # Wait for the result to propagate
    internal_result = int(dut.myCPU.RF1.reg_data[register3].value)
    expected_result = value2 -  value1
    assert internal_result == expected_result, f"ORA test failed: expected {expected_result}, found {internal_result}"

    cocotb.log.info("Simplified ALU SUB operation test passed successfully.")
'''