function showBalance(counter,balance) {
    const balanceElement = document.getElementById(`balance-${counter}`);
    if (balanceElement.innerText === 'xxxxx.xx') {


        
        balanceElement.innerText = balance;
    } else {
        balanceElement.innerText = 'xxxxx.xx';
    }
}
