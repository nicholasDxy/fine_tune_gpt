import os
import re


def get_include_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        include_files = []
    for line in lines:
        if line.startswith('#include'):
            include_file = line.split()
            if len(include_file) < 2:
                continue
            # print(len(include_file))
            include_file = include_file[1].strip(
                '"<>\n').split('\\')[-1].split('/')[-1]
            include_files.append(include_file)
    return include_files


def reduce_item(new_expand, expand_result):
    res = []
    for file in new_expand:
        if file in expand_result:
            continue
        else:
            res.append(file)
    return res


def recursively_expand(file_path, root_dir, max_level=3):
    to_be_expand = []
    expand_result = set()
    to_be_expand.extend(get_include_file(file_path))
    level = 0
    while len(to_be_expand) != 0:
        if level >= max_level:
            break
        count = len(to_be_expand)
        while count > 0:
            file_name = to_be_expand.pop(0)
            expand_result.add(file_name)
            file_name = file_name.split('/')[-1].split('\\')[-1]
            flag = False
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if file == file_name:
                        flag = True
                        include_path = os.path.join(root, file)
                        to_be_expand.extend(reduce_item(
                            get_include_file(include_path), expand_result))
                        break
            if flag == False:
                print(f'Warning: {file_name} not found')
            count -= 1
        level += 1
    print(expand_result)
    return expand_result


def modify_jsonl_file(input_file, output_file, old_text, new_text):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = json.loads(line)
            if 'instr' in data:
                data['instr'] = data['instr'].replace(old_text, new_text)
            json.dump(data, outfile, ensure_ascii=False)
            outfile.write('\n')


def combine_source_code_files(input_file_set, root_dir, out_file):
    with open(out_file, 'w') as out_file:
        for in_file in input_file_set:
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    if file == in_file:
                        with open(os.path.join(root, file), 'r') as read_file:
                            out_file.write('\n code of file {}: \n'.format(file))
                            file_contents = read_file.read()
                            out_file.write(file_contents)
                            
def expand_direct_use(input_file):
    with open(input_file, 'r') as file:
        contents = file.read()
    matches = re.findall(r'\b([A-Za-z0-9_]+)\s*::', contents)
    res = set()
    for content in matches:
        res.add(content + '.h')
    return res
    

if __name__ == '__main__':
    input_file = r'/Users/xyd/code/tune/Yunji-chanofthoughts/ssdpexample-utf8/ExampleCpp/Objects/CreateEntityExamples.cpp'
    root_dir = r'/Users/xyd/code/tune/dataset'
    out_dir = r'/Users/xyd/code/tune/expanded.cpp'
    # expand_set = recursively_expand(input_file, root_dir, 3)
    # combine_source_code_files(expand_set, root_dir, out_dir)
    ex_set = expand_direct_use(input_file)
    combine_source_code_files(ex_set, root_dir, out_dir)
