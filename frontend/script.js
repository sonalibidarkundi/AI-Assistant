// =========================================
// INTUCATE AI ASSISTANT
// Frontend JavaScript
// =========================================


// Vercel backend API URL
// Frontend and backend are hosted on the same Vercel project
const API_BASE_URL = "/api";


// =========================================
// ASK SINGLE QUESTION
// =========================================

async function askQuestion() {

    const questionInput =
        document.getElementById("singleQuestion");

    const answerBox =
        document.getElementById("singleAnswer");

    const responseBox =
        document.getElementById("singleResponse");

    const loading =
        document.getElementById("singleLoading");

    const button =
        document.getElementById("askButton");


    // Get question
    const question = questionInput.value.trim();


    // Validate question
    if (!question) {

        alert("Please enter a question.");

        questionInput.focus();

        return;
    }


    // Show loading
    loading.classList.remove("hidden");

    responseBox.classList.add("hidden");

    button.disabled = true;


    try {

        // Send request to Vercel API
        const response = await fetch(
            `${API_BASE_URL}/ask`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    userInput: question
                })
            }
        );


        // Convert response to JSON
        const data = await response.json();


        // Check for backend error
        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );
        }


        // Display AI response
        answerBox.textContent = data.response;

        responseBox.classList.remove("hidden");


    } catch (error) {

        console.error("Error:", error);

        alert(
            "Unable to get the answer. " +
            "Please try again later."
        );


    } finally {

        // Hide loading
        loading.classList.add("hidden");

        // Enable button
        button.disabled = false;
    }
}


// =========================================
// ASK MULTIPLE QUESTIONS
// =========================================

async function askMultipleQuestions() {

    const questionsInput =
        document.getElementById("multipleQuestions");

    const answersContainer =
        document.getElementById("multipleAnswers");

    const responseBox =
        document.getElementById("multipleResponse");

    const loading =
        document.getElementById("multipleLoading");

    const button =
        document.getElementById("multipleButton");


    // Get textarea value
    const text = questionsInput.value.trim();


    // Validate input
    if (!text) {

        alert("Please enter at least one question.");

        questionsInput.focus();

        return;
    }


    // Convert each line into a question
    const questions = text
        .split("\n")
        .map(question => question.trim())
        .filter(question => question.length > 0);


    // Validate questions
    if (questions.length === 0) {

        alert("Please enter valid questions.");

        return;
    }


    // Show loading
    loading.classList.remove("hidden");

    responseBox.classList.add("hidden");

    answersContainer.innerHTML = "";

    button.disabled = true;


    try {

        // Send request to Vercel API
        const response = await fetch(
            `${API_BASE_URL}/ask-multiple`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    userInputs: questions
                })
            }
        );


        // Convert response to JSON
        const data = await response.json();


        // Check for backend error
        if (!response.ok) {

            throw new Error(
                data.error || "Something went wrong."
            );
        }


        // Display each response
        data.responses.forEach(
            (answer, index) => {

                const answerBox =
                    document.createElement("div");

                answerBox.className =
                    "multiple-answer";


                const title =
                    document.createElement("div");

                title.className =
                    "answer-title";

                title.textContent =
                    `Question ${index + 1}`;


                const questionText =
                    document.createElement("div");

                questionText.textContent =
                    questions[index];


                const answerText =
                    document.createElement("div");

                answerText.style.marginTop = "10px";

                answerText.textContent =
                    answer;


                answerBox.appendChild(title);

                answerBox.appendChild(questionText);

                answerBox.appendChild(answerText);

                answersContainer.appendChild(answerBox);
            }
        );


        // Show response section
        responseBox.classList.remove("hidden");


    } catch (error) {

        console.error("Error:", error);

        alert(
            "Unable to process the questions. " +
            "Please try again later."
        );


    } finally {

        // Hide loading
        loading.classList.add("hidden");

        // Enable button
        button.disabled = false;
    }
}