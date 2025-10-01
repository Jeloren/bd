/** @odoo-module **/

export class Game {
  constructor(baseSize) {
    this.level = 1;
    this.baseSize = baseSize;
    this.size = baseSize;
    this.totalPairs = this.size / 2;
    this.container = document.querySelector(".container");
    this.setup();
  }

  nextLevel() {
    if (this.level < 3) {
      this.level++;
      const side = Math.sqrt(this.size);
      const newSide = side + 2; // рост по квадрату
      this.size = newSide * newSide;
      this.totalPairs = this.size / 2;
      this.editContainer();
      this.setup();
    }
  }

  editContainer() {
    if (this.level === 3) {
      this.container.style.maxWidth = "700px";
    } else if (this.level === 1) {
      this.container.style.maxWidth = "300px";
    } else {
      this.container.style.maxWidth = "500px";
    }
  }

  setup() {
    this.cards = this.generateCards();
    this.flippedCards = [];
    this.matchedPairs = [];
    this.moves = 0;
    this.lockBoard = false;
  }

  generateCards() {
    let pairs = [];
    for (let i = 1; i <= this.size / 2; i++) {
      pairs.push(i);
    }

    let cards = [];
    for (let i = 0; i < pairs.length; i++) {
      cards.push(pairs[i]);
      cards.push(pairs[i]);
    }

    cards = this.shuffleArray(cards);
    return cards;
  }

  shuffleArray(array) {
    for (let i = 0; i < array.length; i++) {
      let randomIndex = Math.floor(Math.random() * array.length);
      let temp = array[i];
      array[i] = array[randomIndex];
      array[randomIndex] = temp;
    }
    return array;
  }

  flipCard(index) {
    if (
      this.lockBoard ||
      this.flippedCards.includes(index) ||
      this.matchedPairs.includes(index)
    ) {
      return false;
    }

    this.flippedCards.push(index);

    if (this.flippedCards.length === 2) {
      this.moves++;
      this.lockBoard = true;

      const [firstIndex, secondIndex] = this.flippedCards;

      if (this.cards[firstIndex] === this.cards[secondIndex]) {
        this.matchedPairs.push(firstIndex, secondIndex);
        this.flippedCards = [];
        this.lockBoard = false;
        return true;
      }

      return false;
    }

    return true;
  }

  resetFlippedCards() {
    this.flippedCards = [];
    this.lockBoard = false;
  }

  isGameComplete() {
    return this.matchedPairs.length === this.size;
  }

  // сброс
  restart() {
    this.setup();
  }
}

export class GameBoard {
  constructor(game) {
    this.game = game;
    this.boardElement = document.getElementById("game-board");
    this.movesElement = document.getElementById("moves");
    this.pairsElement = document.getElementById("pairs");
    this.totalPairsElement = document.getElementById("total-pairs");
    this.winMessageElement = document.getElementById("win-message");
    this.restartButton = document.getElementById("restart-btn");
    this.hoveredCardIndex = null; // индекс карточки под курсором
    this.totalPairsElement.textContent = game.totalPairs;
    this.restartButton.addEventListener("click", () => {
      this.game.restart();
      this.render();
      this.winMessageElement.style.display = "none";
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && e.target !== null) {
        this.handleCardClick(this.hoveredCardIndex);
      }
    });

    this.render();
  }

  render() {
    for (let index = 0; index < this.game.cards.length; index++) {
      let card = this.boardElement.querySelector(
        '[data-index="' + index + '"]'
      );

      const value = this.game.cards[index];

      if (!card) {
        card = document.createElement("div");
        card.className = "card";
        card.dataset.index = index;
        card.dataset.value = value;
        card.tabIndex = 0;
        const cardInner = document.createElement("div");
        cardInner.className = "card-inner";

        const cardFront = document.createElement("div");
        cardFront.className = "card-front";
        cardFront.textContent = "?";

        const cardBack = document.createElement("div");
        cardBack.className = "card-back";
        cardBack.textContent = value;

        cardInner.appendChild(cardFront);
        cardInner.appendChild(cardBack);
        card.appendChild(cardInner);

        card.addEventListener("click", () => this.handleCardClick(index));
        card.addEventListener("mouseover", (ev) => {
          card.style.transform = "scale(1.1)";
          this.hoveredCardIndex = index; // запоминаем на какой карточке мышь
        });
        card.addEventListener("mouseout", () => {
          card.style.transform = "scale(1.0)";
          if (this.hoveredCardIndex === index) {
            this.hoveredCardIndex = null; // убираем если ушли
          }
        });

        this.boardElement.appendChild(card);
      } else {
        // обновляем value, если карта уже есть
        card.dataset.value = value;
        const back = card.querySelector(".card-back");
        if (back) back.textContent = value;
      }
    }

    // настройка сетки под квадрат
    const side = Math.sqrt(this.game.size);
    this.boardElement.style.gridTemplateColumns = `repeat(${side}, 1fr)`;

    this.totalPairsElement.textContent = this.game.totalPairs;
    this.updateStats();
    this.update();
  }

  // обновление статистики
  updateStats() {
    this.movesElement.textContent = this.game.moves;
    this.pairsElement.textContent = this.game.matchedPairs.length / 2;
  }

  handleCardClick(index) {
    this.game.flipCard(index);
    this.update();

    if (this.game.lockBoard && this.game.flippedCards.length === 2) {
      setTimeout(() => {
        this.game.resetFlippedCards();
        this.update();
      }, 800);
    }

    if (this.game.isGameComplete()) {
      setTimeout(() => {
        this.winMessageElement.style.display = "block";

        // переход на следующий уровень
        setTimeout(() => {
          this.winMessageElement.style.display = "none";
          this.game.nextLevel();
          this.render();
        }, 1500);
      }, 300);
    }

    this.updateStats();
  }

  // обновление представления
  update() {
    const cards = this.boardElement.querySelectorAll(".card");

    for (let i = 0; i < cards.length; i++) {
      const card = cards[i];
      const index = parseInt(card.dataset.index);

      card.classList.remove("flipped", "matched");

      if (
        this.game.flippedCards.includes(index) ||
        this.game.matchedPairs.includes(index)
      ) {
        card.classList.add("flipped");

        if (this.game.matchedPairs.includes(index)) {
          card.classList.add("matched");
        }
      }
    }
  }
}
