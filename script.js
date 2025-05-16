// 获取DOM元素
const display = document.getElementById('display');
const buttons = document.querySelectorAll('button');
const calculator = document.querySelector('.calculator');
const calcModeBtn = document.getElementById('calc-mode');
const exchangeModeBtn = document.getElementById('exchange-mode');
const tempModeBtn = document.getElementById('temp-mode');

// 计算器状态变量
let currentInput = '0';       // 当前输入
let previousInput = '';       // 上一次输入
let operation = null;         // 当前操作符
let resetScreen = false;      // 是否需要重置屏幕
let isExchangeMode = false;   // 是否为汇率转换模式
let isTempMode = false;      // 是否为温度转换模式

// 汇率设置（1美元 = 7.1人民币）
const USD_TO_CNY_RATE = 7.1;

// 模式切换函数
function switchMode(mode) {
    isExchangeMode = mode === 'exchange';
    isTempMode = mode === 'temp';
    
    // 移除所有模式类
    calculator.classList.remove('exchange-mode', 'temp-mode');
    calcModeBtn.classList.remove('active');
    exchangeModeBtn.classList.remove('active');
    tempModeBtn.classList.remove('active');
    
    // 设置新的模式
    if (isExchangeMode) {
        calculator.classList.add('exchange-mode');
        exchangeModeBtn.classList.add('active');
    } else if (isTempMode) {
        calculator.classList.add('temp-mode');
        tempModeBtn.classList.add('active');
    } else {
        calcModeBtn.classList.add('active');
    }
    
    clearCalculator();
}

// 温度转换函数
function convertTemperature(temp, toCelsius) {
    if (isNaN(temp)) return '0';
    if (toCelsius) {
        // 华氏度转摄氏度
        return ((temp - 32) * 5 / 9).toFixed(1);
    } else {
        // 摄氏度转华氏度
        return (temp * 9 / 5 + 32).toFixed(1);
    }
}

// 汇率转换函数
function convertCurrency(amount, fromUSD) {
    if (isNaN(amount)) return '0';
    if (fromUSD) {
        // 美元转人民币
        return (amount * USD_TO_CNY_RATE).toFixed(2);
    } else {
        // 人民币转美元
        return (amount / USD_TO_CNY_RATE).toFixed(2);
    }
}

// 更新显示屏
function updateDisplay() {
    display.textContent = currentInput;
}

// 添加数字
function inputDigit(digit) {
    if (resetScreen) {
        currentInput = digit;
        resetScreen = false;
    } else {
        // 如果当前输入是0，则替换它，否则追加
        currentInput = currentInput === '0' ? digit : currentInput + digit;
    }
}

// 添加小数点
function inputDecimal() {
    // 如果需要重置屏幕，则先重置为0
    if (resetScreen) {
        currentInput = '0';
        resetScreen = false;
    }
    // 如果当前输入中没有小数点，则添加小数点
    if (!currentInput.includes('.')) {
        currentInput += '.';
    }
}

// 处理操作符
function handleOperator(nextOperator) {
    const inputValue = parseFloat(currentInput);
    
    // 如果已经有待处理的操作，先计算结果
    if (operation && resetScreen) {
        // 只更新操作符，不进行计算
        operation = nextOperator;
        return;
    }
    
    // 如果没有上一次输入，则将当前输入保存为上一次输入
    if (previousInput === '') {
        previousInput = currentInput;
    } else if (operation) {
        // 计算结果
        const result = calculate();
        currentInput = String(result);
        previousInput = currentInput;
    }
    
    resetScreen = true;
    operation = nextOperator;
}

// 计算结果
function calculate() {
    const prev = parseFloat(previousInput);
    const current = parseFloat(currentInput);
    
    if (isNaN(prev) || isNaN(current)) return '';
    
    let result = 0;
    switch (operation) {
        case '+':
            result = prev + current;
            break;
        case '-':
            result = prev - current;
            break;
        case '×':
            result = prev * current;
            break;
        case '÷':
            // 处理除以0的情况
            if (current === 0) {
                alert('错误：不能除以0');
                clearCalculator();
                return '0';
            }
            result = prev / current;
            break;
        default:
            return current;
    }
    
    // 处理小数点后过多的位数
    return Math.round(result * 1000000) / 1000000;
}

// 处理等号
function handleEquals() {
    // 如果没有操作符，则不进行计算
    if (!operation) return;
    
    const result = calculate();
    currentInput = String(result);
    previousInput = '';
    operation = null;
    resetScreen = true;
}

// 清除计算器
function clearCalculator() {
    currentInput = '0';
    previousInput = '';
    operation = null;
    resetScreen = false;
}

// 退格功能
function handleBackspace() {
    if (currentInput.length === 1 || (currentInput.length === 2 && currentInput.startsWith('-'))) {
        currentInput = '0';
    } else {
        currentInput = currentInput.slice(0, -1);
    }
}

// 为所有按钮添加点击事件
buttons.forEach(button => {
    button.addEventListener('click', () => {
        // 根据按钮ID执行相应操作
        switch (button.id) {
            case 'calc-mode':
                switchMode('calc');
                break;
            case 'exchange-mode':
                switchMode('exchange');
                break;
            case 'temp-mode':
                switchMode('temp');
                break;
            case 'usd-to-cny':
                if (isExchangeMode) {
                    const amount = parseFloat(currentInput);
                    currentInput = convertCurrency(amount, true);
                    resetScreen = true;
                }
                break;
            case 'cny-to-usd':
                if (isExchangeMode) {
                    const amount = parseFloat(currentInput);
                    currentInput = convertCurrency(amount, false);
                    resetScreen = true;
                }
                break;
            case 'c-to-f':
                if (isTempMode) {
                    const temp = parseFloat(currentInput);
                    currentInput = convertTemperature(temp, false);
                    resetScreen = true;
                }
                break;
            case 'f-to-c':
                if (isTempMode) {
                    const temp = parseFloat(currentInput);
                    currentInput = convertTemperature(temp, true);
                    resetScreen = true;
                }
                break;
            case 'clear':
                clearCalculator();
                break;
            case 'backspace':
                handleBackspace();
                break;
            case 'equals':
                handleEquals();
                break;
            case 'decimal':
                inputDecimal();
                break;
            case 'add':
                handleOperator('+');
                break;
            case 'subtract':
                handleOperator('-');
                break;
            case 'multiply':
                handleOperator('×');
                break;
            case 'divide':
                handleOperator('÷');
                break;
            default:
                // 数字按钮
                if (button.classList.contains('key-number')) {
                    const digit = button.textContent;
                    inputDigit(digit);
                }
        }
        
        updateDisplay();
    });
});

// 添加键盘支持
document.addEventListener('keydown', (event) => {
    if (isExchangeMode && event.key === 'Enter') {
        // 在汇率模式下，Enter键默认执行美元到人民币的转换
        event.preventDefault();
        const amount = parseFloat(currentInput);
        currentInput = convertCurrency(amount, true);
        resetScreen = true;
        updateDisplay();
        return;
    }
    // 数字键 0-9
    if (/^\d$/.test(event.key)) {
        event.preventDefault();
        inputDigit(event.key);
        updateDisplay();
    }
    
    // 操作符
    switch (event.key) {
        case '+':
            event.preventDefault();
            handleOperator('+');
            break;
        case '-':
            event.preventDefault();
            handleOperator('-');
            break;
        case '*':
            event.preventDefault();
            handleOperator('×');
            break;
        case '/':
            event.preventDefault();
            handleOperator('÷');
            break;
        case '.':
        case ',':
            event.preventDefault();
            inputDecimal();
            break;
        case '=':
        case 'Enter':
            event.preventDefault();
            handleEquals();
            break;
        case 'Backspace':
            event.preventDefault();
            handleBackspace();
            break;
        case 'Escape':
        case 'Delete':
            event.preventDefault();
            clearCalculator();
            break;
    }
    
    updateDisplay();
});

// 初始化显示
updateDisplay();
