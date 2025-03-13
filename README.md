## Sales Forecasting Project Using Python

This is my Python sales forecasting project log. This repository serves as a detailed record of my learning journey, showcasing the techniques I've studied and applied to forecast weekly sales effectively.

### Overview

In this project, I explore:

- Weekly sales forecasting using Python.
- Incorporating external factors such as Digital Ads, Offline Ads, TV commercials (TVCM), and Print Media into predictive models.
- Comparing various forecasting approaches including Linear Regression, Prophet, LightGBM, and SARIMAX.

### Dataset

The data used in this project includes:

- **Minimum Requirements:**
  - At least 2 years of weekly sales data.
  - Future values for external factors such as Digital Ads, Offline Ads, TVCM, and Print Media.

- Weekly Sales figures.
- External advertising metrics:
  - Digital Ads
  - Offline Ads
  - TVCM (Gross Rating Points)
  - Print Media spend

The data was cleaned and preprocessed to ensure reliability for model building.

### Modeling Techniques

I've explored the following forecasting methods:

- **Linear Regression (OLS)**:

  - Basic relationship modeling between sales and external variables.

- **Prophet**:

  - Developed by Facebook for forecasting data with strong seasonal patterns and external factors.

- **LightGBM**:

  - A machine learning model that efficiently captures complex, non-linear interactions between variables.

- **SARIMAX (Seasonal ARIMA with external regressors)**:

  - Combines traditional ARIMA with external regressors to capture seasonal effects and external influences.


### Performance Comparison

I evaluated each model using these metrics:

- **Root Mean Squared Error (RMSE)**:
  - Assesses prediction accuracy by penalizing larger errors significantly.

- **Mean Absolute Error (MAE)**:
  - Indicates average absolute differences between predictions and actual results.

- **Mean Absolute Percentage Error (MAPE)**:
  - Provides an easy-to-interpret percentage measure of prediction accuracy.

### Insights and Observations

Each forecasting model was compared against benchmarks, such as historical averages, to highlight incremental improvements from advanced modeling techniques. I've included visualizations and analyses that help clearly understand each model's strengths and weaknesses.


### Learning Log Structure

The project includes step-by-step code with explanations to:

- Prepare and clean data.
- Implement and optimize models using hyperparameter tuning.
- Evaluate model performance visually and numerically.

Feel free to review my notes and adapt my learnings to your own projects.


### Project Deliverables

- Detailed, commented Python scripts.
- Comprehensive Jupyter Notebook outlining my learning journey.
- Clear visualizations comparing forecasted and actual sales.


This log captures my learning experience in sales forecasting, serving as a reference and guide for further exploration and application.

