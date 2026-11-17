// Interactive Environmental Awareness Quiz Engine
const quizQuestions = [
  {
    question: "1. Which toxic heavy metal found in CRT monitors and soldered circuit boards causes severe neurological damage?",
    options: [
      "Lead (Pb)",
      "Iron (Fe)",
      "Aluminum (Al)",
      "Calcium (Ca)"
    ],
    answer: 0,
    explanation: "Lead (Pb) is widely used in solder and vintage CRT funnels (up to 2-3 kg per CRT). It is a potent neurotoxin that impairs brain development and causes kidney dysfunction."
  },
  {
    question: "2. Why should spent lithium-ion batteries NEVER be disposed of in standard municipal garbage bins?",
    options: [
      "They make the garbage bag too heavy",
      "They can experience thermal runaway and spark uncontrollable compaction truck or landfill fires",
      "Municipal workers only collect plastic items",
      "Batteries dissolve instantly in rain without harm"
    ],
    answer: 1,
    explanation: "Lithium-ion batteries contain flammable organic electrolytes. Physical compaction in municipal garbage trucks punctures cells, causing thermal runaway and dangerous fires reaching over 1,000°C."
  },
  {
    question: "3. What is the crucial safety practice recommended before storing or recycling any loose battery?",
    options: [
      "Washing it with soapy water",
      "Taping both positive (+) and negative (-) terminals with non-conductive electrical tape",
      "Puncturing the outer casing to release pressure",
      "Freezing it in the refrigerator"
    ],
    answer: 1,
    explanation: "Taping terminals prevents accidental contact with other metals, preventing short circuits that lead to sparks and combustion."
  },
  {
    question: "4. What does EPR stand for under the Ministry of Environment E-Waste (Management) Rules?",
    options: [
      "Electronic Product Registry",
      "Extended Producer Responsibility",
      "Environmental Pollution Reduction",
      "Eco Plastic Recycling"
    ],
    answer: 1,
    explanation: "Extended Producer Responsibility (EPR) mandates that electronic manufacturers and brand owners are legally responsible for financing and organizing the channelization and recycling of their end-of-life products."
  },
  {
    question: "5. Why is 'Urban Mining' considered superior to traditional virgin ore mining?",
    options: [
      "1 tonne of discarded smartphones contains up to 50 times more gold than 1 tonne of raw mined gold ore",
      "Urban mining requires no specialized tools",
      "Raw gold mining causes zero environmental disturbance",
      "Electronics do not contain any real metals"
    ],
    answer: 0,
    explanation: "E-waste is a concentrated secondary ore. Extracting gold, silver, copper, and palladium from circuit boards consumes 80% less energy and emits far less carbon than mining virgin earth."
  },
  {
    question: "6. Which toxic element commonly found in laptop backlights and fluorescent display lamps can vaporize at room temperature?",
    options: [
      "Mercury (Hg)",
      "Titanium (Ti)",
      "Zinc (Zn)",
      "Copper (Cu)"
    ],
    answer: 0,
    explanation: "Mercury in Cold Cathode Fluorescent Lamps (CCFL) easily vaporizes into the air if screens are broken, posing severe inhalation risks and bioaccumulating in aquatic food chains."
  },
  {
    question: "7. Why is burning insulated copper cables in the open air illegal and hazardous?",
    options: [
      "It makes the copper wires brittle",
      "It burns the polyvinyl chloride (PVC) sheath, releasing carcinogenic dioxins and furans into the atmosphere",
      "It takes too long to ignite",
      "It creates unpleasant smoke that only smells bad without toxic chemicals"
    ],
    answer: 1,
    explanation: "Burning PVC cables produces chlorinated dioxins, furans, and hydrochloric acid fumes—some of the most toxic carcinogens known to science. Authorized recyclers use mechanical wire granulators instead."
  },
  {
    question: "8. What should you always do with personal smartphones and laptops prior to e-waste recycling?",
    options: [
      "Submerge them in vinegar",
      "Perform a full cryptographic Factory Data Reset and remove SIM/SD cards to safeguard personal data",
      "Break the motherboard in half with a hammer",
      "Paint the screen black"
    ],
    answer: 1,
    explanation: "A cryptographic factory data reset overwrites encryption keys, preventing unauthorized recovery of sensitive personal documents, photos, and financial logins."
  },
  {
    question: "9. Which official statutory bodies regulate and authorize e-waste dismantlers and recyclers in India?",
    options: [
      "CPCB (Central Pollution Control Board) and State Pollution Control Boards (e.g., KSPCB)",
      "Automobile Manufacturers Association",
      "International Postal Union",
      "Consumer Electronics Show (CES)"
    ],
    answer: 0,
    explanation: "The Central Pollution Control Board (CPCB) and State Boards such as KSPCB issue official authorization, track material balance sheets, and audit environmental emission standards."
  },
  {
    question: "10. What is the fundamental principle of the Circular Electronics Economy?",
    options: [
      "Extracting resources, using once, and dumping immediately in oceans",
      "Designing for longevity, repair, component reuse, and closed-loop material recycling to minimize virgin extraction",
      "Replacing all smartphones every 6 months",
      "Banning all electronic devices permanently"
    ],
    answer: 1,
    explanation: "The circular economy keeps components and materials at their highest utility and value at all times, drastically reducing landfill burden and ecological devastation."
  }
];

let currentQuestionIndex = 0;
let userScore = 0;
let selectedOption = null;
let answered = false;

document.addEventListener('DOMContentLoaded', function () {
  const quizContainer = document.getElementById('quizContainer');
  if (!quizContainer) return;

  renderQuestion();

  const nextBtn = document.getElementById('quizNextBtn');
  if (nextBtn) {
    nextBtn.addEventListener('click', function () {
      if (!answered) {
        if (selectedOption === null) {
          alert('Please select an answer to proceed.');
          return;
        }
        checkAnswer();
      } else {
        currentQuestionIndex++;
        if (currentQuestionIndex < quizQuestions.length) {
          renderQuestion();
        } else {
          showResults();
        }
      }
    });
  }
});

function renderQuestion() {
  answered = false;
  selectedOption = null;
  const q = quizQuestions[currentQuestionIndex];

  // Update Progress
  const progressPercent = ((currentQuestionIndex) / quizQuestions.length) * 100;
  const progressBar = document.getElementById('quizProgressBar');
  if (progressBar) progressBar.style.width = `${progressPercent}%`;

  const questionNumEl = document.getElementById('quizQuestionNum');
  if (questionNumEl) questionNumEl.textContent = `Question ${currentQuestionIndex + 1} of ${quizQuestions.length}`;

  const questionTextEl = document.getElementById('quizQuestionText');
  if (questionTextEl) questionTextEl.textContent = q.question;

  const optionsContainer = document.getElementById('quizOptionsContainer');
  if (optionsContainer) {
    optionsContainer.innerHTML = '';
    q.options.forEach((opt, idx) => {
      const optDiv = document.createElement('div');
      optDiv.className = 'quiz-option';
      optDiv.innerHTML = `
        <span class="badge bg-secondary rounded-circle px-2 py-1">${String.fromCharCode(65 + idx)}</span>
        <span>${opt}</span>
      `;
      optDiv.addEventListener('click', function () {
        if (answered) return;
        document.querySelectorAll('.quiz-option').forEach(el => el.classList.remove('selected'));
        optDiv.classList.add('selected');
        selectedOption = idx;
      });
      optionsContainer.appendChild(optDiv);
    });
  }

  const feedbackBox = document.getElementById('quizFeedbackBox');
  if (feedbackBox) feedbackBox.classList.add('d-none');

  const nextBtn = document.getElementById('quizNextBtn');
  if (nextBtn) {
    nextBtn.textContent = 'Submit Answer';
    nextBtn.className = 'btn btn-success px-4';
  }
}

function checkAnswer() {
  answered = true;
  const q = quizQuestions[currentQuestionIndex];
  const options = document.querySelectorAll('.quiz-option');

  if (selectedOption === q.answer) {
    userScore++;
    options[selectedOption].classList.remove('selected');
    options[selectedOption].classList.add('correct');
  } else {
    options[selectedOption].classList.remove('selected');
    options[selectedOption].classList.add('incorrect');
    options[q.answer].classList.add('correct');
  }

  // Display explanation
  const feedbackBox = document.getElementById('quizFeedbackBox');
  if (feedbackBox) {
    feedbackBox.innerHTML = `
      <div class="alert ${selectedOption === q.answer ? 'alert-success' : 'alert-warning'} mb-0">
        <h6 class="fw-bold mb-1">${selectedOption === q.answer ? '<i class="fa-solid fa-circle-check me-2 text-success"></i>Correct!' : '<i class="fa-solid fa-circle-xmark me-2 text-danger"></i>Incorrect'}</h6>
        <p class="mb-0 small">${q.explanation}</p>
      </div>
    `;
    feedbackBox.classList.remove('d-none');
  }

  const nextBtn = document.getElementById('quizNextBtn');
  if (nextBtn) {
    nextBtn.textContent = currentQuestionIndex === quizQuestions.length - 1 ? 'View Final Results' : 'Next Question';
    nextBtn.className = 'btn btn-primary px-4';
  }
}

function showResults() {
  const quizCard = document.getElementById('quizCard');
  const resultsCard = document.getElementById('quizResultsCard');
  if (quizCard) quizCard.classList.add('d-none');
  if (resultsCard) resultsCard.classList.remove('d-none');

  const scoreText = document.getElementById('quizFinalScore');
  if (scoreText) scoreText.textContent = `${userScore} / ${quizQuestions.length}`;

  const pct = (userScore / quizQuestions.length) * 100;
  const titleEl = document.getElementById('quizBadgeTitle');
  const msgEl = document.getElementById('quizBadgeMessage');

  if (pct >= 80) {
    if (titleEl) titleEl.textContent = '🌟 Master Eco-Champion';
    if (msgEl) msgEl.textContent = 'Outstanding! You possess exemplary knowledge of e-waste hazards, circular recovery, and environmental safety regulations!';
  } else if (pct >= 60) {
    if (titleEl) titleEl.textContent = '🌿 Green Guardian';
    if (msgEl) msgEl.textContent = 'Great work! You understand essential e-waste hazards and proper disposal protocols. Keep spreading public awareness!';
  } else {
    if (titleEl) titleEl.textContent = '🌱 Environmental Learner';
    if (msgEl) msgEl.textContent = 'Good effort! Review the Proper Disposal Guidelines and Awareness sections to sharpen your e-waste management skills.';
  }

  // Dynamic certificate name input binding
  const certNameInput = document.getElementById('certNameInput');
  const certNameDisplay = document.getElementById('certNameDisplay');
  const certDateDisplay = document.getElementById('certDateDisplay');

  if (certDateDisplay) {
    certDateDisplay.textContent = new Date().toLocaleDateString('en-US', {
      year: 'numeric', month: 'long', day: 'numeric'
    });
  }

  if (certNameInput && certNameDisplay) {
    certNameInput.addEventListener('input', function () {
      certNameDisplay.textContent = this.value.trim() || 'Valued Participant';
    });
  }
}

