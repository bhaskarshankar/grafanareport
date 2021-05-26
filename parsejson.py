import re

dictionary = {}


def parse_json_recursively(json_object , target_key) :
    if type ( json_object ) is dict and json_object :
        for key in json_object :
           # print(json_object [ 'title' ])

            if key == target_key :
                if ('targets' in json_object.keys ( ) and 'title' in json_object.keys ( )) :
                    metrickey = re.sub ( '[^A-Za-z0-9]+' , '' , json_object [ 'title' ] )
                    if metrickey not in dictionary :
                        value = json_object [ key ]
                        print ( "id {}: {} {}".format ( target_key , metrickey , value ) )
                        dictionary [ metrickey ] = value


                else:
                    continue

            parse_json_recursively ( json_object [ key ] , target_key )

    elif type ( json_object ) is list and json_object :
        for item in json_object :
            parse_json_recursively ( item , target_key )
    return dictionary
