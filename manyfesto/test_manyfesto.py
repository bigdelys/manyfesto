import unittest

num_tests = 11


class TestManyfesto(unittest.TestCase):
    def test_manyfesto(self):

        # deal with path issues
        import os
        from pathlib import Path
        manyfesto_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        import sys
        if manyfesto_path not in sys.path:  # add parent dir to paths
            print('Adding ', manyfesto_path, "to system path.")
            sys.path.append(manyfesto_path)

        import oyaml
        from manyfesto import read

        print('\n-------------- Tests Output -----------------')
        for test_num in range(num_tests):
            test_folder = Path(manyfesto_path) / Path(r"tests/test" + str(test_num) + "/")
            container_folder = test_folder / 'container'
            correct_read_file = test_folder / Path('correct_output.yaml')
            output = read(container_folder.as_posix())
            with correct_read_file.open('r') as f:
                correct_read_odict = oyaml.safe_load(f)
            assert output == correct_read_odict, "Error in matching Test " + str(test_num) + " output: \n %s" % \
                                                 oyaml.dump(output, default_flow_style=False)
            print("Ran test " + str(test_num) + ".")


if __name__ == '__main__':
    unittest.main()