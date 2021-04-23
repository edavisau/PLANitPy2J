import os, sys   
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..','src'))

import gc
import unittest
import math
from test_utils import PlanItHelper
from planit import *

class TestSuite(unittest.TestCase):
    
    def test_converter_network_reader(self):
        INPUT_PATH = os.path.join('converter', 'osm')
        OUTPUT_PATH = os.path.join(INPUT_PATH, 'matsim')
        COUNTRY = "Australia"
        FULL_INPUT_FILE_NAME = os.path.join(INPUT_PATH, "sydneycbd.osm.pbf")
        
        # no correspondence to Java test as we explicitly test non-failure of Python code to instantiate converters
        plan_it = PLANit()
        
        # network converter
        converter_factory = plan_it.converterFactory
        network_converter = converter_factory.create(ConverterType.NETWORK)
        
        # osm reader        
        osm_reader = network_converter.create_reader(NetworkReaderType.OSM, COUNTRY)
        osm_reader.get_settings.set_input_file(FULL_INPUT_FILE_NAME)
        
        #writer
        osm_writer = network_converter.create_writer(NetworkReaderType.MATSIM)
        osm_writer.get_settings.set_output_directory(OUTPUT_PATH)
        osm_writer.get_settings.set_country(COUNTRY)
        
        # perform conversion
        network_converter.convert(osm_reader,osm_writer)    

    def test_explanatory_report_zero_outputs(self):
        project_path = os.path.join('explanatory', 'reportZeroOutputs')
        plan_it = PLANit(project_path)

        description = "explanatory"
        csv_file_name = "Time_Period_1_2.csv"
        od_csv_file_name = "Time_Period_1_1.csv"
        xml_file_name = "Time_Period_1.xml"
        max_iterations = 500
        epsilon = 0.0000000001
        
        PlanItHelper.run_test_with_zero_flow_outputs(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name, project_path))
        gc.collect()
        
    def test_explanatory_with_memory_output(self):
        # Explanatory unit test, which saves results to memory only and not to file, to test contents of memory output formatter are correct
        
        print("Running test_explanatory with results only stored in memory")
        description = "explanatory";
        max_iterations = 2
        epsilon = 0.001
        plan_it = PLANit()
        plan_it = PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, deactivate_file_output=True)

        mode_xml_id = "1"
        time_period_xml_id = "0"
        
        flow_position = plan_it.memory.get_position_of_output_value_property(OutputType.LINK, OutputProperty.FLOW)
        cost_position = plan_it.memory.get_position_of_output_value_property(OutputType.LINK, OutputProperty.LINK_COST)
        length_position = plan_it.memory.get_position_of_output_value_property(OutputType.LINK, OutputProperty.LENGTH)
        speed_position = plan_it.memory.get_position_of_output_value_property(OutputType.LINK, OutputProperty.CALCULATED_SPEED)
        capacity_position = plan_it.memory.get_position_of_output_value_property(OutputType.LINK, OutputProperty.CAPACITY_PER_LANE)
        number_of_lanes_position = plan_it.memory.get_position_of_output_value_property(OutputType.LINK, OutputProperty.NUMBER_OF_LANES)
        
        memory_output_iterator_link = plan_it.memory.iterator(mode_xml_id, time_period_xml_id, max_iterations, OutputType.LINK)
        while memory_output_iterator_link.has_next():
            memory_output_iterator_link.next()
            keys = memory_output_iterator_link.get_keys()
            values = memory_output_iterator_link.get_values()
            self.assertEqual(values[flow_position], 1)
            self.assertTrue(math.isclose(values[cost_position], 10, rel_tol=0.001))
            self.assertEqual(values[length_position], 10)
            self.assertEqual(values[capacity_position], 2000)
            self.assertEqual(values[number_of_lanes_position], 1)
 
        path_position = plan_it.memory.get_position_of_output_value_property(OutputType.PATH, OutputProperty.PATH_STRING)
        key1_position = plan_it.memory.get_position_of_output_key_property(OutputType.PATH, OutputProperty.ORIGIN_ZONE_XML_ID)
        key2_position = plan_it.memory.get_position_of_output_key_property(OutputType.PATH, OutputProperty.DESTINATION_ZONE_XML_ID)
        memory_output_iterator_path = plan_it.memory.iterator(mode_xml_id, time_period_xml_id, max_iterations, OutputType.PATH)
        while memory_output_iterator_path.has_next():
            memory_output_iterator_path.next()
            keys = memory_output_iterator_path.get_keys()
            self.assertTrue(keys[key1_position] in ["1","2"])
            self.assertTrue(keys[key2_position] in ["1","2"])
            values = memory_output_iterator_path.get_values()
            value = values[path_position]
            if ((keys[key1_position] == "1") and (keys[key2_position] == "2")):
                self.assertEqual(value,"[1,2]")
            else:
                self.assertEqual(value, "")
                                
        od_position = plan_it.memory.get_position_of_output_value_property(OutputType.OD, OutputProperty.OD_COST)
        key1_position = plan_it.memory.get_position_of_output_key_property(OutputType.OD, OutputProperty.ORIGIN_ZONE_XML_ID)
        key2_position = plan_it.memory.get_position_of_output_key_property(OutputType.OD, OutputProperty.DESTINATION_ZONE_XML_ID)
        memory_output_iterator_od = plan_it.memory.iterator(mode_xml_id, time_period_xml_id, max_iterations-1, OutputType.OD)
        while memory_output_iterator_od.has_next():
            memory_output_iterator_od.next()
            keys = memory_output_iterator_od.get_keys()
            self.assertTrue(keys[key1_position] in ["1","2"])
            self.assertTrue(keys[key2_position] in ["1","2"])
            values = memory_output_iterator_od.get_values()
            value = values[od_position]
            if ((keys[key1_position] == "1") and (keys[key2_position] == "2")):
                self.assertEqual(value,10)
            else:
                self.assertEqual(value, "")
       
        gc.collect()
 
    def test_explanatory(self):
        # corresponds to testExplanatory() in Java
        
        print("Running test_explanatory with default project path")
        description = "explanatory";
        csv_file_name = "Time_Period_1_2.csv";
        od_csv_file_name = "Time_Period_1_1.csv";
        xml_file_name = "Time_Period_1.xml";
        max_iterations = 500
        epsilon = 0.001
        plan_it = PLANit()
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name))
        gc.collect()
    
    def test_explanatory_without_activating_outputs(self):
        #Explanatory unit test, which does not activate the output type configurations directly, but relies on the code to do this automatically (corresponds to testExplanatory() in Java)
        #    Includes test that OD csv output file has not been created, since this OutputType.OD was deactivated
        
        print("Running test_explanatory with default project path")
        description = "explanatory";
        csv_file_name = "Time_Period_1_2.csv";
        od_csv_file_name = "Time_Period_1_1.csv";
        xml_file_name = "Time_Period_1.xml";
        max_iterations = 500
        epsilon = 0.001
        plan_it = PLANit()
        plan_it = PlanItHelper.run_test_without_activating_outputs(plan_it, max_iterations, epsilon, description, 1)
        
        output_type = OutputType.OD
        output_type_instance = GatewayState.python_2_java_gateway.entry_point.createEnum(output_type.java_class_name(), output_type.value)
        self.assertTrue(plan_it.assignment.is_output_type_active(output_type_instance))
        plan_it.assignment.deactivate_output(OutputType.OD)
        self.assertFalse(plan_it.assignment.is_output_type_active(output_type_instance))
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name))
        project_path = os.getcwd()
        od_file_name = PlanItHelper.create_full_file_name(OutputType.OD, project_path, description,  od_csv_file_name)
        self.assertFalse(os.path.exists(od_file_name))
        gc.collect()        

    def test_2_SIMO_MISO_route_choice_single_mode_with_initial_costs_and_one_iteration_and_three_time_periods(self):
        #corresponds to test_2_SIMO_MISO_route_choice_single_mode_with_initial_costs_and_one_iteration_and_three_time_periods() in Java)
        
        print("Running test_2_SIMO_MISO_route_choice_single_mode_with_initial_costs_and_one_iteration_and_three_time_periods")
        project_path = os.path.join('route_choice', 'xml', 'SIMOMISOrouteChoiceInitialCostsOneIterationThreeTimePeriods')
        plan_it = PLANit(project_path)
        description = "test2initialCostsOneIterationThreeTimePeriods"
        csv_file_name1 = "Time_Period_1_1.csv"
        od_csv_file_name1 = "Time_Period_1_0.csv"
        csv_file_name2 = "Time_Period_2_1.csv"
        od_csv_file_name2 = "Time_Period_2_0.csv"
        csv_file_name3 = "Time_Period_3_1.csv"
        od_csv_file_name3 = "Time_Period_3_0.csv"
        xml_file_name1 = "Time_Period_1.xml"
        xml_file_name2 = "Time_Period_2.xml"
        xml_file_name3 = "Time_Period_3.xml"
        max_iterations = 1
        timePeriod0XmlId="0"
        timePeriod1XmlId="1"
        timePeriod2XmlId="2"
        plan_it.initial_cost.set(os.path.join("route_choice", "xml", "SIMOMISOrouteChoiceInitialCostsOneIterationThreeTimePeriods", "initial_link_segment_costs_time_period_1.csv"), timePeriod0XmlId)
        plan_it.initial_cost.set(os.path.join("route_choice", "xml", "SIMOMISOrouteChoiceInitialCostsOneIterationThreeTimePeriods", "initial_link_segment_costs_time_period_2.csv"), timePeriod1XmlId)
        plan_it.initial_cost.set(os.path.join("route_choice", "xml", "SIMOMISOrouteChoiceInitialCostsOneIterationThreeTimePeriods", "initial_link_segment_costs_time_period_3.csv"), timePeriod2XmlId)
        epsilon = 0.001
        
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name3, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name3, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name3, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name3, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name3, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name3, project_path))
        gc.collect()
                      
    def test_5_SIMO_MISO_route_choice_two_modes(self):
        #corresponds to test_5_SIMO_MISO_route_choice_two_modes() in Java

        # prep
        project_path = os.path.join('route_choice', 'xml', 'SIMOMISOrouteChoiceTwoModes')
        plan_it = PLANit(project_path)
        description = "testRouteChoice5"
        csv_file_name = "Time_Period_1_500.csv"
        od_csv_file_name = "Time_Period_1_499.csv"
        xml_file_name = "Time_Period_1.xml"
        max_iterations = 500
        epsilon = 0.0000000001
        output_type_configuration_option=1
                
        # setup
        plan_it.set(TrafficAssignment.TRADITIONAL_STATIC)         
        plan_it.assignment.physical_cost.set_default_parameters(0.8, 4.5, "2", "1")
        
        plan_it.assignment.output_configuration.set_persist_only_final_Iteration(True)
        plan_it.assignment.activate_output(OutputType.LINK)
        plan_it.assignment.link_configuration.remove(OutputProperty.TIME_PERIOD_XML_ID)
        plan_it.assignment.link_configuration.remove(OutputProperty.TIME_PERIOD_ID)
        plan_it.assignment.link_configuration.remove(OutputProperty.MAXIMUM_SPEED)
  
        plan_it.assignment.activate_output(OutputType.OD)
        plan_it.assignment.od_configuration.deactivate(ODSkimSubOutputType.NONE)
        plan_it.assignment.od_configuration.remove(OutputProperty.TIME_PERIOD_XML_ID)
        plan_it.assignment.od_configuration.remove(OutputProperty.RUN_ID)
        plan_it.assignment.activate_output(OutputType.PATH)
        plan_it.assignment.path_configuration.set_path_id_type(PathIdType.NODE_XML_ID)
        plan_it.assignment.gap_function.stop_criterion.set_max_iterations(max_iterations)
        plan_it.assignment.gap_function.stop_criterion.set_epsilon(epsilon)
         
        plan_it.output.set_xml_name_root(description)                
        plan_it.output.set_csv_name_root(description)     
        plan_it.output.set_output_directory(project_path)
        plan_it.run()        
        
        # compare
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name, project_path))
        gc.collect()
    
    def test_2_SIMO_MISO_route_choice_single_mode_with_initial_costs_and_500_iterations(self):
        # Unit test for route 2 with initial costs and 500 iterations (corresponds to test_2_SIMO_MISO_route_choice_single_mode_with_initial_costs_and_500_iterations() in Java)

        project_path = os.path.join('route_choice', 'xml', 'SIMOMISOrouteChoiceSingleModeWithInitialCosts500Iterations')
        plan_it = PLANit(project_path)
        description = "testRouteChoice2initialCosts"
        csv_file_name = "Time_Period_1_500.csv"
        od_csv_file_name = "Time_Period_1_499.csv"
        xml_file_name = "Time_Period_1.xml"
        plan_it.initial_cost.set(os.path.join("route_choice", "xml", "SIMOMISOrouteChoiceSingleModeWithInitialCosts500Iterations", "initial_link_segment_costs.csv"))
        max_iterations = 500
        epsilon = 0.0000000001
        
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name, project_path))
        gc.collect()
        
    def test_4_bi_directional_links_route_choice_single_mode_with_two_time_periods(self):
        # corresponds to test_4_bi_directional_links_route_choice_single_mode_with_two_time_periods() in Java
        
        print("Running test_route_choice_compare_with_OmniTRANS4_using_two_time_periods")
        project_path = os.path.join('route_choice', 'xml', 'biDirectionalLinksRouteChoiceSingleModeWithTwoTimePeriods')
        plan_it = PLANit(project_path)
        description = "testRouteChoice42"
        csv_file_name1 = "Time_Period_1_500.csv"
        od_csv_file_name1 = "Time_Period_1_499.csv"
        csv_file_name2 = "Time_Period_2_500.csv"
        od_csv_file_name2 = "Time_Period_2_499.csv"
        xml_file_name1 = "Time_Period_1.xml"
        xml_file_name2 = "Time_Period_2.xml"
        max_iterations = 500
        epsilon = 0.0
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name2, project_path))
        gc.collect()        
        
    def test_mode_test(self):
        #corresponds to test_mode_test() in Java

        project_path = os.path.join('mode_test', 'xml', 'simple')
        plan_it = PLANit(project_path)
        description = "mode_test"
        csv_file_name = "Time_Period_1_2.csv"
        od_csv_file_name = "Time_Period_1_1.csv"
        xml_file_name = "Time_Period_1.xml"
        max_iterations = 2
        epsilon = 0.0000000001
        
        # setup
        plan_it.set(TrafficAssignment.TRADITIONAL_STATIC)         
        plan_it.assignment.output_configuration.set_persist_only_final_Iteration(True)
        plan_it.assignment.activate_output(OutputType.LINK)
        plan_it.assignment.link_configuration.remove(OutputProperty.TIME_PERIOD_XML_ID)
        plan_it.assignment.link_configuration.remove(OutputProperty.TIME_PERIOD_ID)
        plan_it.assignment.link_configuration.remove(OutputProperty.MAXIMUM_SPEED)
  
        plan_it.assignment.activate_output(OutputType.OD)
        plan_it.assignment.od_configuration.deactivate(ODSkimSubOutputType.NONE)
        plan_it.assignment.od_configuration.remove(OutputProperty.TIME_PERIOD_XML_ID)
        plan_it.assignment.od_configuration.remove(OutputProperty.RUN_ID)
        plan_it.assignment.activate_output(OutputType.PATH)
        plan_it.assignment.path_configuration.set_path_id_type(PathIdType.NODE_XML_ID)
        plan_it.assignment.gap_function.stop_criterion.set_max_iterations(max_iterations)
        plan_it.assignment.gap_function.stop_criterion.set_epsilon(epsilon)
         
        plan_it.output.set_xml_name_root(description)                
        plan_it.output.set_csv_name_root(description)     
        plan_it.output.set_output_directory(project_path)
                
        plan_it.assignment.physical_cost.set_default_parameters(0.8, 4.5, "1", "1")
        link_segment_xml_id = "3"
        mode_xml_id = "1" 
        plan_it.assignment.physical_cost.set_parameters(1.0, 5.0, mode_xml_id, link_segment_xml_id)       
                
        plan_it.run()        
        
        # tests
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name, project_path))        
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name, project_path))
        gc.collect()        

    def test_basic_shortest_path_algorithm_a_to_c(self):
        # corresponds to test_basic_shortest_path_algorithm_a_to_c() in Java)
        
        print("Running test_basic_shortest_path_algorithm_a_to_c")
        project_path = os.path.join('basicShortestPathAlgorithm', 'xml', 'AtoC')
        plan_it = PLANit(project_path)
        description = "testBasic2";
        csv_file_name = "Time_Period_1_2.csv";
        od_csv_file_name = "Time_Period_1_1.csv";
        xml_file_name = "Time_Period_1.xml";
        max_iterations = 500
        epsilon = 0.001
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name, project_path))
        gc.collect()
        
    def test_basic_shortest_path_algorithm_a_to_d(self):
        # corresponds to test_basic_shortest_path_algorithm_a_to_d() in Java
        
        print("Running test_basic_shortes_path_algorithm_a_to_d")
        project_path = os.path.join('basicShortestPathAlgorithm', 'xml', 'AtoD')
        plan_it = PLANit(project_path)
        description = "testBasic3";
        csv_file_name = "Time_Period_1_2.csv";
        od_csv_file_name = "Time_Period_1_1.csv";
        xml_file_name = "Time_Period_1.xml";
        max_iterations = 500
        epsilon = 0.001
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name, project_path))
        gc.collect()        
   
    def test_basic_shortest_path_algorithm_three_time_periods(self):
        # corresponds to test_basic_shortest_path_algorithm_three_time_periods() in Java)
        
        print("Running test_basic_three_time_periods")
        project_path = os.path.join('basicShortestPathAlgorithm', 'xml', 'ThreeTimePeriods')
        plan_it = PLANit(project_path)
        description = "testBasic13"
        csv_file_name1 = "Time_Period_1_2.csv"
        csv_file_name2 = "Time_Period_2_2.csv"
        csv_file_name3 = "Time_Period_3_2.csv"
        od_csv_file_name1 = "Time_Period_1_1.csv"
        od_csv_file_name2 = "Time_Period_2_1.csv"
        od_csv_file_name3 = "Time_Period_3_1.csv"
        xml_file_name1 = "Time_Period_1.xml"
        xml_file_name2 = "Time_Period_2.xml"
        xml_file_name3 = "Time_Period_3.xml"
        max_iterations = 500
        epsilon = 0.001
        PlanItHelper.run_test(plan_it, max_iterations, epsilon, description, 1, project_path)
        
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.LINK, description, xml_file_name3, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.LINK, description, csv_file_name3, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.PATH, description, xml_file_name3, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.PATH, description, csv_file_name3, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name1, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name1, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name2, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name2, project_path))
        PlanItHelper.delete_file(OutputType.OD, description, xml_file_name3, project_path)
        self.assertTrue(PlanItHelper.compare_csv_files_and_clean_up(OutputType.OD, description, od_csv_file_name3, project_path))
        gc.collect()   
                
if __name__ == '__main__':
    unittest.main()
    