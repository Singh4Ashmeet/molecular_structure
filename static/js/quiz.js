/**
 * quiz.js – Molecular Theory Explained
 * Question bank, randomisation, rendering, scoring, and save-score API call.
 */

/* ═══════════════════════════════════════════════════════════
   QUESTION BANK
   Each question: { q, options: [str], answer: index (0-based) }
   ═══════════════════════════════════════════════════════════ */
const QUESTION_BANK = {

  Easy: [
    {
      q: "What is the molecular geometry of H₂O?",
      options: ["Linear", "Bent", "Tetrahedral", "Trigonal planar"],
      answer: 1
    },
    {
      q: "How many lone pairs does the oxygen atom have in water?",
      options: ["0", "1", "2", "3"],
      answer: 2
    },
    {
      q: "What is the bond angle in a perfectly tetrahedral molecule?",
      options: ["90°", "104.5°", "109.5°", "120°"],
      answer: 2
    },
    {
      q: "Which of the following molecules is linear?",
      options: ["H₂O", "NH₃", "CO₂", "CH₄"],
      answer: 2
    },
    {
      q: "VSEPR theory is used to predict:",
      options: ["Molecular colour", "Molecular mass", "Molecular shape", "Reaction rate"],
      answer: 2
    },
    {
      q: "How many bonds does carbon form in methane (CH₄)?",
      options: ["2", "3", "4", "6"],
      answer: 2
    },
    {
      q: "What shape does NH₃ have?",
      options: ["Linear", "Bent", "Trigonal pyramidal", "Tetrahedral"],
      answer: 2
    },
    {
      q: "Is water (H₂O) a polar or non-polar molecule?",
      options: ["Non-polar", "Polar", "Ionic", "Metallic"],
      answer: 1
    },
    {
      q: "Which molecule has NO lone pairs on its central atom?",
      options: ["H₂O", "NH₃", "CH₄", "HF"],
      answer: 2
    },
    {
      q: "What does VSEPR stand for?",
      options: [
        "Valence Shell Electron Pair Repulsion",
        "Variable Shell Electron Pair Reaction",
        "Valence Sigma Electron Pair Rotation",
        "Volume Shell Electron Pair Repulsion"
      ],
      answer: 0
    }
  ],

  Medium: [
    {
      q: "Why is the H–O–H bond angle in water 104.5° and not 109.5°?",
      options: [
        "Carbon atoms reduce the angle",
        "Two lone pairs on O compress the bond angle",
        "Hydrogen atoms are too large",
        "The molecule is linear"
      ],
      answer: 1
    },
    {
      q: "What is the electron geometry of NH₃?",
      options: ["Bent", "Trigonal pyramidal", "Tetrahedral", "Linear"],
      answer: 2
    },
    {
      q: "CO₂ has polar C=O bonds yet is non-polar overall. Why?",
      options: [
        "C and O have identical electronegativity",
        "The molecule is bent, so dipoles cancel",
        "The linear shape causes the two dipoles to cancel",
        "CO₂ has lone pairs that neutralise polarity"
      ],
      answer: 2
    },
    {
      q: "What is the order of repulsion strength in VSEPR theory?",
      options: [
        "Bond–Bond > Lone–Bond > Lone–Lone",
        "Lone–Lone > Lone–Bond > Bond–Bond",
        "Lone–Bond > Bond–Bond > Lone–Lone",
        "All repulsions are equal"
      ],
      answer: 1
    },
    {
      q: "How many lone pairs does nitrogen have in NH₃?",
      options: ["0", "1", "2", "3"],
      answer: 1
    },
    {
      q: "The bond angle in NH₃ is approximately:",
      options: ["90°", "107°", "109.5°", "120°"],
      answer: 1
    },
    {
      q: "Which molecule has the smallest bond angle?",
      options: ["CH₄ (109.5°)", "NH₃ (107°)", "H₂O (104.5°)", "CO₂ (180°)"],
      answer: 2
    },
    {
      q: "What determines the molecular geometry of a molecule according to VSEPR?",
      options: [
        "Only the number of bonding pairs",
        "Only the number of lone pairs",
        "Both bonding pairs and lone pairs around the central atom",
        "The mass of the atoms"
      ],
      answer: 2
    },
    {
      q: "In which molecule do bond dipoles cancel to give a non-polar molecule?",
      options: ["H₂O", "NH₃", "HCl", "CO₂"],
      answer: 3
    },
    {
      q: "The electron geometry and molecular geometry of CH₄ are both:",
      options: ["Linear", "Bent", "Trigonal pyramidal", "Tetrahedral"],
      answer: 3
    }
  ],

  Hard: [
    {
      q: "A molecule has 2 bonding pairs and 2 lone pairs on the central atom. What is its molecular geometry?",
      options: ["Linear", "Bent", "Tetrahedral", "Trigonal pyramidal"],
      answer: 1
    },
    {
      q: "Why does water have a higher boiling point than expected for its molecular mass?",
      options: [
        "Water has a large molecular mass",
        "Water forms extensive hydrogen bonds due to its polarity",
        "Water is a non-polar molecule",
        "Water has no lone pairs"
      ],
      answer: 1
    },
    {
      q: "A central atom with 3 bonding pairs and 1 lone pair has which molecular geometry?",
      options: ["Trigonal planar", "Tetrahedral", "Trigonal pyramidal", "Bent"],
      answer: 2
    },
    {
      q: "Which statement correctly explains why CH₄ is non-polar?",
      options: [
        "C–H bonds are polar and their dipoles cancel due to tetrahedral symmetry",
        "C–H bonds are non-polar and there are no lone pairs",
        "Carbon is not electronegative",
        "Methane has lone pairs that neutralise the dipoles"
      ],
      answer: 0
    },
    {
      q: "What limitation does VSEPR theory have?",
      options: [
        "It cannot predict shapes for simple molecules",
        "It fails to account for lone pairs",
        "It cannot reliably predict geometry for transition metal complexes",
        "It only applies to ionic compounds"
      ],
      answer: 2
    },
    {
      q: "If a molecule has a tetrahedral electron geometry and 2 lone pairs, what is its molecular shape?",
      options: ["Bent", "Linear", "Trigonal pyramidal", "Tetrahedral"],
      answer: 0
    },
    {
      q: "The difference between electron geometry and molecular geometry is:",
      options: [
        "Electron geometry includes lone pairs; molecular geometry does not",
        "Molecular geometry includes lone pairs; electron geometry does not",
        "They are always the same",
        "Electron geometry applies only to non-polar molecules"
      ],
      answer: 0
    },
    {
      q: "Why does each additional lone pair on the central atom reduce bond angles by roughly 2–2.5°?",
      options: [
        "Lone pairs have larger mass than bond pairs",
        "Lone pairs occupy more angular space due to attraction by only one nucleus",
        "Lone pairs are negatively charged overall",
        "Lone pairs increase the electronegativity of the central atom"
      ],
      answer: 1
    },
    {
      q: "Which of these molecules exhibits hydrogen bonding?",
      options: ["CH₄", "CO₂", "NH₃", "CCl₄"],
      answer: 2
    },
    {
      q: "In VSEPR, a molecule with 5 electron domains and 2 lone pairs has which molecular geometry?",
      options: ["Trigonal bipyramidal", "T-shaped", "Seesaw", "Linear"],
      answer: 1
    }
  ]
};

/* ═══════════════════════════════════════════════════════════
   STATE
   ═══════════════════════════════════════════════════════════ */
let currentDifficulty = null;
let currentQuestions  = [];
let userAnswers       = [];  // array of selected option indices (null = unanswered)
let submitted         = false;

/* ═══════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════ */

/** Fisher–Yates shuffle – returns a new shuffled array */
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** Pick n random items from an array */
function pickRandom(arr, n) {
  return shuffle(arr).slice(0, n);
}

/* ═══════════════════════════════════════════════════════════
   QUIZ FLOW
   ═══════════════════════════════════════════════════════════ */

/** Called by difficulty buttons */
function startQuiz(difficulty) {
  currentDifficulty = difficulty;
  currentQuestions  = pickRandom(QUESTION_BANK[difficulty], 5);
  userAnswers       = new Array(5).fill(null);
  submitted         = false;

  // Highlight active difficulty button
  document.querySelectorAll('.diff-btn').forEach(function (b) {
    b.classList.remove('active');
  });
  const map = { Easy: 'easy', Medium: 'medium', Hard: 'hard' };
  document.querySelectorAll('.diff-btn').forEach(function (b) {
    const text = b.textContent.trim();
    if (text.includes(difficulty)) b.classList.add('active', map[difficulty]);
  });

  // Show quiz area, hide score
  document.getElementById('quizArea').classList.add('visible');
  document.getElementById('scoreCard').classList.remove('visible');
  document.getElementById('quizDiffLabel').textContent = difficulty + ' Difficulty';

  renderQuestions();
}

/** Render all 5 question cards */
function renderQuestions() {
  const container = document.getElementById('questionsContainer');
  container.innerHTML = '';

  currentQuestions.forEach(function (q, qi) {
    const card = document.createElement('div');
    card.className = 'question-card';
    card.id = 'qcard-' + qi;

    let optionsHTML = '<ul class="options-list">';
    q.options.forEach(function (opt, oi) {
      optionsHTML += `
        <li>
          <label class="option-label" id="lbl-${qi}-${oi}" onclick="selectOption(${qi}, ${oi})">
            <input type="radio" name="q${qi}" value="${oi}" />
            <span class="option-dot"></span>
            <span>${opt}</span>
          </label>
        </li>`;
    });
    optionsHTML += '</ul>';

    card.innerHTML = `
      <div class="question-number">Question ${qi + 1} of 5</div>
      <div class="question-text">${q.q}</div>
      ${optionsHTML}`;

    container.appendChild(card);
  });

  // Show submit button
  const actions = document.getElementById('quizActions');
  actions.style.display = 'flex';
}

/** Called when user clicks an option */
function selectOption(qi, oi) {
  if (submitted) return;

  userAnswers[qi] = oi;

  // Update visual selection for this question
  for (let i = 0; i < currentQuestions[qi].options.length; i++) {
    const lbl = document.getElementById('lbl-' + qi + '-' + i);
    if (lbl) lbl.classList.toggle('selected', i === oi);
  }
}

/** Submit the quiz */
function submitQuiz() {
  // Check all answered
  const unanswered = userAnswers.filter(function (a) { return a === null; }).length;
  if (unanswered > 0) {
    alert('Please answer all ' + unanswered + ' remaining question(s) before submitting.');
    return;
  }

  submitted = true;
  let score = 0;

  // Reveal correct / wrong
  currentQuestions.forEach(function (q, qi) {
    const correct = q.answer;
    const chosen  = userAnswers[qi];

    for (let i = 0; i < q.options.length; i++) {
      const lbl = document.getElementById('lbl-' + qi + '-' + i);
      if (!lbl) continue;
      lbl.classList.remove('selected');
      if (i === correct) lbl.classList.add('correct');
      if (i === chosen && chosen !== correct) lbl.classList.add('wrong');
    }

    if (chosen === correct) score++;
  });

  // Hide submit button
  document.getElementById('quizActions').style.display = 'none';

  // Show score card after a short delay
  setTimeout(function () {
    showScore(score);
  }, 800);

  // Save score to backend
  saveScore(currentDifficulty, score);
}

/** Display score card */
function showScore(score) {
  document.getElementById('quizArea').classList.remove('visible');

  const card    = document.getElementById('scoreCard');
  const circle  = document.getElementById('scoreCircle');
  const message = document.getElementById('scoreMessage');
  const sub     = document.getElementById('scoreSub');

  circle.textContent = score + '/5';

  const pct = score / 5;
  if (pct === 1)       { message.textContent = '🏆 Perfect Score!';    sub.textContent = 'Outstanding! You nailed every question.'; }
  else if (pct >= 0.8) { message.textContent = '🎉 Excellent!';         sub.textContent = 'Great work — almost perfect!'; }
  else if (pct >= 0.6) { message.textContent = '👍 Good Job!';          sub.textContent = 'Solid understanding. Keep studying!'; }
  else if (pct >= 0.4) { message.textContent = '📚 Keep Practising!';   sub.textContent = 'Review the material and try again.'; }
  else                 { message.textContent = '💡 Needs More Study';   sub.textContent = 'Don\'t give up — check the Learn section!'; }

  // Colour the circle by score
  circle.style.borderColor = pct >= 0.6 ? 'var(--teal)' : pct >= 0.4 ? '#ffb400' : '#ff4455';
  circle.style.color       = circle.style.borderColor;

  card.classList.add('visible');
}

/** Re-run the same difficulty */
function retryQuiz() {
  startQuiz(currentDifficulty);
}

/** Go back to difficulty selection */
function changeDifficulty() {
  document.getElementById('quizArea').classList.remove('visible');
  document.getElementById('scoreCard').classList.remove('visible');
  document.getElementById('questionsContainer').innerHTML = '';
  document.querySelectorAll('.diff-btn').forEach(function (b) {
    b.classList.remove('active', 'easy', 'medium', 'hard');
  });
  currentDifficulty = null;
}

/** POST score to /save-score */
function saveScore(difficulty, score) {
  fetch('/save-score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ difficulty: difficulty, score: score })
  })
  .then(function (r) { return r.json(); })
  .then(function (data) {
    if (data.status === 'saved') {
      console.log('Score saved:', difficulty, score);
    }
  })
  .catch(function (err) {
    console.warn('Could not save score:', err);
  });
}
