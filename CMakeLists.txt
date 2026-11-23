cmake_minimum_required(VERSION 3.20)
project(SimoderModExamples VERSION 0.1.0 LANGUAGES NONE)

# @summary Install existing authoring examples at the legacy relative package paths.
install(DIRECTORY examples/ DESTINATION examples
    PATTERN cache EXCLUDE PATTERN __pycache__ EXCLUDE PATTERN "*.pyc" EXCLUDE)
install(FILES LICENSE README.md sdk.lock.json DESTINATION licenses/Simoder-Mod-Examples)

set(SIMODER_SDK_SOURCE_DIR "" CACHE PATH "Optional explicit canonical SDK checkout for provenance validation")
include(CTest)
if(BUILD_TESTING)
    find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
    add_test(NAME examples_sdk_provenance
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_sdk_provenance.py"
            --sdk-source "${SIMODER_SDK_SOURCE_DIR}")
    add_test(NAME examples_contract
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_examples.py")
    if(SIMODER_SDK_SOURCE_DIR)
        add_test(NAME examples_sdk_integrity
            COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_sdk_integrity.py"
                --sdk-source "${SIMODER_SDK_SOURCE_DIR}"
                --work-dir "${CMAKE_CURRENT_BINARY_DIR}/examples-sdk-integrity")
        set_tests_properties(examples_sdk_integrity PROPERTIES TIMEOUT 120)
    else()
        message(STATUS "examples_sdk_integrity NOT_RUN: explicit clean SIMODER_SDK_SOURCE_DIR required")
    endif()
    add_test(NAME examples_install_layout
        COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_examples.py"
            --install-build "${CMAKE_CURRENT_BINARY_DIR}")
endif()
