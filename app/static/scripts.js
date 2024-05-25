var timeLeft = 25;
var timerElement = document.getElementById('timer');
var form = document.getElementById('questionForm');
var dice = document.getElementById('dice');
var diceContainer = document.querySelector('.dice-container');

var timer = setInterval(function () {
    if (timeLeft <= 0) {
        clearInterval(timer);
        form.submit();
    } else {
        timerElement.textContent = 'زمان باقی‌مانده: ' + timeLeft + ' ثانیه';
    }
    timeLeft -= 1;
}, 1000);

form.addEventListener('submit', function(event) {
    event.preventDefault();
    diceContainer.style.display = 'flex';
    rollDice();
});

function rollDice() {
    const roll = Math.floor(Math.random() * 6) + 1;
    dice.textContent = roll;
    animateDice(roll);
}

function animateDice(roll) {
    dice.classList.add('rolling');
    setTimeout(() => {
        dice.classList.remove('rolling');
        submitFormWithDiceValue(roll);
    }, 1000);
}

function submitFormWithDiceValue(roll) {
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'dice_roll';
    input.value = roll;
    form.appendChild(input);

    setTimeout(() => {
        form.submit();
    }, 1000);
}