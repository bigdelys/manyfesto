from unittest import TestCase

num_tests = 11

class TestManyfesto(TestCase):
    def test_manyfesto(self):
        from manyfesto import read
        import oyaml
        from pathlib import Path
        print('\n-------------- Tests Output -----------------')
        for test_num in range(num_tests):
            test_folder = Path(r"../tests/test" + str(test_num) + "/")
            container_folder = test_folder / 'container'
            correct_read_file = test_folder / Path('correct_output.yaml')
            output = read(container_folder)
            with correct_read_file.open('r') as f:
                correct_read_odict = oyaml.safe_load(f)
            assert output == correct_read_odict, "Error in matching Test " + str(test_num) + " output: \n %s" % \
                                                 oyaml.dump(output, default_flow_style=False)
            print("Ran test 1-" + str(test_num) + ".")
