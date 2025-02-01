pip install numpy scipy

import numpy as np
from scipy.optimize import minimize

# Sample data: 
# 'responses' = 1 for correct answer, 0 for incorrect
# 'difficulties' = difficulty level of the questions answered by the student
responses = np.array([1, 1, 1, 1, 0])  # Example: correct/incorrect answers for 5 questions
difficulties = np.array([2, 1, 1, 2, 3])  # Example: difficulty levels for 5 questions

# Rasch model probability function
def rasch_probability(ability, difficulty):
    """Calculates the probability of a correct response given ability and difficulty."""
    return 1 / (1 + np.exp(difficulty - ability))

# Negative log-likelihood function
def neg_log_likelihood(ability, responses, difficulties):
    """Calculates the negative log-likelihood for the Rasch model."""
    probabilities = rasch_probability(ability, difficulties)
    # The likelihood is higher if correct answers match the model's predicted probabilities
    likelihood = responses * np.log(probabilities) + (1 - responses) * np.log(1 - probabilities)
    return -np.sum(likelihood)

# Function to estimate ability using MLE (Maximum Likelihood Estimation)
def estimate_ability(responses, difficulties):
    """Estimates student ability using maximum likelihood estimation (MLE)."""
    initial_guess = 0  # Start with an initial ability guess
    result = minimize(neg_log_likelihood, initial_guess, args=(responses, difficulties), method='BFGS')
    return result.x[0]  # Estimated ability

# Run the ability estimation
estimated_ability = estimate_ability(responses, difficulties)
print(f"Estimated Student Ability: {estimated_ability}")
