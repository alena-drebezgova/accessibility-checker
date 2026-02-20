*** Settings ***
Library     Browser
Library     squash_tf.TFParamService



*** Test Cases ***
Test Eight Components
    ${parameter}=    Get Global Param    target_base_url    http:localhost:8080/sut/
