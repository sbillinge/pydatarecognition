# Put user data here to test user data reader.
#
# the pattern is as follows
# testuserdata_contents_expecteds = [(file_1_as_string, file_1_as_list_of_strings),
#                                    (file_2_as_string, file_2_as_list_of_strings),
#                                    ...
#                                    ]
# where the expected outputs are lists of strings.

testuserdata_contents_expecteds = [
    ("\
10.043\t2037.0\n\
10.0913\t2212.0\n\
10.1413\t2155.0\n\
"
    ,
    ["10.0413\t2037.0\n",
     "10.0913\t2212.0\n",
     "10.1413\t2155.0\n"
    ]
    )
]
