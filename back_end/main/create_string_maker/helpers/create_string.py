def create_string(clusters, titles, constant_dict):
    statement = '''string = ""
     '''
    statements = [statement]

    for cluster in clusters:
        statement = '''\ni = 0
position=0
for key in variable_map:'''
        if 'required_tags' in cluster and len(cluster['required_tags']) > 0:
            statement+=f'''\n\tif not set(variable_options[key]) & {{ {','.join("'" + str(element) + "'" for element in cluster['required_tags'])} }}:
            i=i+1
            continue
            '''
        if 'skip_tags' in cluster and len(cluster['skip_tags']) > 0:
            statement+=f'''\n\tif set(variable_options[key]) & {{ {','.join("'" + str(element) + "'" for element in cluster['skip_tags'])} }}:
            i=i+1
            continue'''
        statement+='''\n\ti = i + 1\n\tif 1 == 0:
        continue
        '''
        statements.append(statement)
        for keyword_type, group in cluster.items():
            if not isinstance(keyword_type, frozenset):
                continue
            # If no keyword, just append the raw segment
            if keyword_type == frozenset([0]):
                static_text = ''.join(map(str, group))
                modified_segment = ''.join(group[0]['segment'])

                statement = f'\nstring = string + """ {modified_segment} """\n'
                statements.pop()
                statements.append(statement)
            if all(item >= 20000 for item in keyword_type):
                group['segment'] = ''.join(map(str, group['segment']))
                for key_type in keyword_type:
                    if 20000 <= key_type < 30000:
                        try:
                            corresponding_key = next(key for key, value in constant_dict.items() if value == key_type)
                            index = titles.index(str(corresponding_key))
                        except ValueError:
                            continue  # If the keyword_type is not found in titles, continue with the next iteration
                        group['segment'] = group['segment'].replace(
                            str(key_type), f'""" + title[{index}] + """')
                    else:
                        group['segment'] = group['segment'].replace(
                            str(key_type), '""" +  " YOU_NEED_REPLACEMENT_HERE "  + """')
                modified_segment = group['segment']
                statement = f'\nstring = string + """ {modified_segment} """\n'
                statements.pop()
                statements.append(statement)
            else:
                group['segment'] = ''.join(map(str, group['segment']))
                for key_type in keyword_type:
                    if 20000 <= key_type < 30000:
                        try:
                            corresponding_key = next(key for key, value in constant_dict.items() if value == key_type)
                            index = titles.index(str(corresponding_key))
                        except ValueError:
                            continue  # If the keyword_type is not found in titles, continue with the next iteration
                        group['segment'] = group['segment'].replace(
                            str(key_type), f'""" + title[{index}] + """')
                    elif key_type >= 30000:
                        group['segment'] = group['segment'].replace(
                            str(keyword_type), '""" +  " YOU_NEED_REPLACEMENT_HERE "  + """')
                    else:
                        unique_keyword_type = key_type

                keyword_type = unique_keyword_type
                modified_segment = group['segment'].replace("'", "\\'").replace('"', '\\"').replace(str(keyword_type), '""" +  key  + """')
                if cluster['unique_keywords'] is None:
                    main_statement = f'''\n\telif variable_map[key] == {keyword_type}:
            result = """{modified_segment}""" '''
                else:
                    main_statement = f'''\n\telif variable_map[key] == {keyword_type}:
            result = """{modified_segment}""" '''
                statements.append(main_statement)



        if 'left_end_pos' in cluster:
            first_position = cluster['left_end_pos']
            last_position = cluster['right_end_pos']
            else_check = ''
            if 10000 in cluster:
                modified_segment = ''.join(cluster[10000]['segment']).replace('"', '\\"').replace('10000', '""" +  key  + """')
                # modified_segment = ''.join(cluster[10000]['segment']).replace(str(keyword_type), "keyword")
                else_check = f'''\n\telse:
         result = """{modified_segment}""" '''

            if_statement = "\n\n\tif 1 == 0:\n\t\tcontinue"

            if cluster['regex_replace_map'] and 'first_vs_middle' in cluster['regex_replace_map'] and len(cluster['regex_replace_map']['first_vs_middle']) > 0:
                first_item = f'\n\telif i == 1:'
                for regex_replacement in cluster['regex_replace_map']['first_vs_middle']:
                    pattern = regex_replacement[0]
                    replacement = regex_replacement[1]
                    first_item += f'\n\t\tresult = re.sub("{pattern}", "{replacement}", result, count=1)'
            else:
                first_item = ""

            if first_position is not None and len(cluster['regex_replace_map']['left_end_vs_middle']) > 0:
                lower_limit_check = f'\n\telif position <= {first_position}:'
                for regex_replacement in cluster['regex_replace_map']['left_end_vs_middle']:
                    pattern = regex_replacement[0]
                    replacement = regex_replacement[1]
                    lower_limit_check += f'\n\t\tresult = re.sub("{pattern}", "{replacement}", result, count=1)'
            else:
                lower_limit_check = ""


            if cluster['regex_replace_map'] and 'last_vs_middle' in cluster['regex_replace_map'] and len(cluster['regex_replace_map']['last_vs_middle']) > 0:
                last_item = f'\n\telif i == len(variable_map):'
                for regex_replacement in cluster['regex_replace_map']['last_vs_middle'][::-1]:
                    pattern = regex_replacement[0]
                    replacement = regex_replacement[1]
                    last_item += f'\n\t\tresult = re.sub("{pattern}", "{replacement}", result[::-1], count=1)[::-1]'
                last_item += f'\n\t\tposition = -len(result)'
            else:
                last_item = ""

            if last_position is not None and len(cluster['regex_replace_map']['right_end_vs_middle']) > 0:
                upper_limit_check = f'\n\telif position >= {last_position}:'
                for regex_replacement in cluster['regex_replace_map']['right_end_vs_middle'][::-1]:
                    pattern = regex_replacement[0]
                    replacement = regex_replacement[1]
                    upper_limit_check += f'\n\t\tresult = re.sub("{pattern}", "{replacement}", result[::-1], count=1)[::-1]'
                upper_limit_check += f'\n\t\tposition = -len(result)'

            else:
                upper_limit_check = ""



            assign_statement = '''\n\tstring = string + result
            '''
            statement = else_check + if_statement + first_item + lower_limit_check + if_statement + last_item + upper_limit_check + assign_statement
            statements.append(statement)
            statements.append("\n\tposition = position + len(result)")

    return ''.join(statements) + "\nreturn string"


def is_in_keys(value, dictionary):
    return any(value in key for key in dictionary.keys() if isinstance(key, frozenset))


def get_value(element, dictionary):
    for key, value in dictionary.items():
        if element in key:
            return value
    return None  # or some default value if the element is not found in any key