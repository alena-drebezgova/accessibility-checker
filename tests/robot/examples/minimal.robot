*** Settings ***
Library         Browser
Library         AccessibilityCheckerLibrary

Test Setup      Start Browser and Login    http://localhost:8080/sut/


*** Test Cases ***
Accessibility Lighthouse
    Make Lighthouse Check
    Click    table
    Type Text    id=search-input    table
    Make Lighthouse Check

Accessibility Axe Core
    Make Axe Core Check
    Click    table
    Type Text    id=search-input    table
    Make Axe Core Check

Accessibility IBM Equal Access Accessibility Checker
    Make IBM Equal Access Check
    Click    table
    Type Text    id=search-input    table
    Make IBM Equal Access Check

Accessibility Global Accessibility Reporting Tool
    Make Global Accessibility Check
    Click    table
    Type Text    id=search-input    table
    Make Global Accessibility Check


*** Keywords ***
Start Browser and Login
    [Arguments]    ${url}
    New Browser    chromium
    New Context
    New Page    ${url}
    Login User    ironman    1234567890

Login User
    Type Text    id=username    admin
    Type Text    id=password    admin
    Click Button    id=login-button
    Wait For Navigation
