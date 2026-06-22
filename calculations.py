# ==============================================================================
# GLOBAL VARIABLES AND ARRAYS PART
# ==============================================================================
ATMOSPHERIC_PRESSURE_KPA = 101.325
my_array1 = [1, 2, 3, 4, 5, 6, 7, 8]
my_array2 = [22, 33, 44, 55, 66, 77, 88, 99]
my_array3 = [88, 99, 111, 222, 333, 444, 555, 666]


# ==============================================================================
# CALCULATION FUNCTIONS (DEF) PART
# ==============================================================================

def PV_404_PI_FC_Out_W(signals, attributes):
    first_val = my_array1[0]
    second_val = my_array2[1]
    voltage = signals.get("PV_402_VI_FC_Out_V", 0.0)  # 0.0 its default value to prevent the crash on TB
    calculated_power = first_val * second_val
    return calculated_power

def PVC_303_DP_Clt_Stk_kPaa(signals, attributes):
    total_sum = sum(my_array1)
    p_inlet  = signals.get("PV_302_PI_Clt_Stk_In_kPaa", 0.0)
    p_outlet = signals.get("PV_303_PI_Clt_Stk_Out_kPaa", 0.0)
    return (p_inlet - p_outlet) + total_sum

def SV_501_PC_FC_Usr_Dmd_W(signals, attributes):
    array_modifier = my_array3[2]
    demand = attributes.get("Power_Demand", 0.0)
    calculated_demand = demand + array_modifier
    return calculated_demand