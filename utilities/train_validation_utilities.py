from imports import *
from config import *

######################
# --- PARAMETERS --- #
######################

'''
Description: Get the splitting parameters based on the split type
Args:
    split_type: The type of split to be performed
Returns:
    dict: A dictionary containing the splitting parameters
'''
def get_splitting_params(split_type):
    if split_type == BS:
        # Block splits time series
        params = {'split_type': BS,
                  'splits': 5} # Number of splits to be performed
    elif split_type == WFS:
        # Walk forward splits time series
        params = {'split_type': WFS,
                  'min_obser': 20000, # Minimum number of observations 
                  'sliding_window': 5000} # Sliding window size 
    elif split_type == SS:
        # Single split time series
        params = {'split_type': SS,
                  'split_label': 'months', # Split label [weeks | months | years]
                  'split_value': 1} # Split value (number of weeks, months or years)
    else:
        raise ValueError("Invalid split type")

    return params

'''
Description: Returns the default parameters of the selected model
Args:
    model_name: Name of the selected model
Returns: 
    params: Dictionary of default parameters for the selected model
'''
def get_defaults_model_params(model_name):
    if model_name == LR:
        params = {
            'maxIter': [100],
            'regParam': [0.0],
            'elasticNetParam': [0.0]
        }   
    elif model_name == GLR:
        params = {
            'maxIter': [25],
            'regParam': [0]
        }
    elif model_name == RF:
        params = {
            'numTrees': [20],
            'maxDepth': [5],
            'seed': [RANDOM_SEED]
        }
    elif model_name == GBTR:
        params = {
            'maxIter': [20],
            'maxDepth': [5],
            'stepSize': [0.1],
            'seed': [RANDOM_SEED]
        }
    
    return params

'''
Description: Return the parameters grid of the selected model
Args:
    model_name: Name of the selected model
Returns: 
    params: Dictionary of the parameters grid of the selected model
'''
def get_model_grid_params(model_name):
    if (model_name == LR):
        params = {
            'maxIter' : [5, 10, 50, 80, 100], # The maximum number of iterations to use, in range [1, inf)
            'regParam' : np.arange(0,1,0.2).round(decimals=2), # The regularization parameter, in range [0, inf)
            'elasticNetParam' : np.arange(0,1,0.2).round(decimals=2) # the ElasticNet mixing parameter, in range [0, 1]. For alpha = 0, the penalty is an L2 penalty. For alpha = 1, it is an L1 penalty
        }
    if (model_name == GLR):
        params = {
            'maxIter' : [5, 10, 50, 80], # The maximum number of iterations to use, in range [1, inf)
            'regParam' : [0, 0.1, 0.2], # The regularization parameter, in range [0, inf)
            'family': ['gaussian', 'gamma'], # The name of family which is a description of the error distribution to be used in the model. Supported options: "gaussian", "binomial", "poisson", "gamma" and "tweedie"
            'link': ['log', 'identity', 'inverse'] # The name of link function which provides the relationship between the linear predictor and the mean of the distribution function. Supported options: "identity", "log", "inverse", "logit", "probit", "cloglog" and "sqrt"
        }
    elif (model_name == RF):
        params = {
            'numTrees' : [3, 5, 10, 20, 30], # Number of trees to train (>= 1) 
            'maxDepth' : [3, 5, 10], # Maximum depth of the tree (>= 0)
            'seed' : [RANDOM_SEED]
        }
    elif (model_name == GBTR):
        params = {
            'maxIter' : [3, 5, 10, 20, 30], # Number of trees to train (>= 1)
            'maxDepth' : [3, 5, 10], # Maximum depth of the tree (>= 0)
            'stepSize': [0.1, 0.3, 0.5, 0.7], # Step size (a.k.a. learning rate) in interval (0, 1] for shrinking the contribution of each estimator
            'seed' : [RANDOM_SEED]
        }

    return params

'''
Description: Return the best model parameters based on the scoring mechanism
Args:
    parameters: DataFrame containing the parameters and corresponding scores
Return: 
    grouped_scores: DataFrame with the average scores for each unique set of parameters
    best_params: Tuple representing the parameters with the highest final score
'''
def choose_best_params(parameters):
    # Calculate the weight of each value in the "Splits" column
    parameters['Split weight'] = parameters['Splits'].rank(ascending=True)

    # Normalize the split weights to a scale of 0 to 1
    parameters['Split weight'] = parameters['Split weight'] / parameters['Split weight'].max()
    
    # Normalize the RMSE values to a scale of 0 to 1
    rmse_weight = 1 - (parameters['RMSE'] / parameters['RMSE'].max())

    # Add the RMSE weight as a new column
    parameters['RMSE weight'] = rmse_weight
    
    # Convert the values in the "Parameters" column to tuples
    parameters['Parameters'] = parameters['Parameters'].apply(tuple)

    # Calculate the frequency of each unique value in the "Parameters" column
    freq = parameters['Parameters'].value_counts(normalize=True)

    # Normalize the frequencies to a scale of 0 to 1
    freq_norm = freq / freq.max()

    # Create a new column called "Frequency weight" with the normalized frequencies
    parameters['Frequency weight'] = parameters['Parameters'].map(freq_norm)

    # Group the rows by the "Parameters" column and calculate the average of the other columns
    grouped_scores = parameters[['Parameters', 'Split weight', 'RMSE weight', "Frequency weight"]].groupby('Parameters').mean()
    
    # Calculate the final score for each row
    grouped_scores['Final score'] = grouped_scores['Frequency weight'] *  grouped_scores['Split weight'] * grouped_scores['RMSE weight']

    # Sort the DataFrame by the "Final score" column in descending order
    grouped_scores = grouped_scores.sort_values(by='Final score', ascending=False)

    # Get the index of the row with the highest final score
    best_params = grouped_scores['Final score'].idxmax()

    return grouped_scores, best_params
    
'''
Description: Returns the best model parameters
Args:
    parameters: Parameters to be entered in the parameter grid of the selected model
    model_name: Name of the selected model
Return: 
    params: Parameters list of the selected model
'''
def get_best_model_params(parameters, model_name):
    if (model_name == LR):
        params = {
            'maxIter' : [parameters[0]],
            'regParam' : [parameters[1]],
            'elasticNetParam' : [parameters[2]]
        }   
    if (model_name == GLR):
        params = {
            'maxIter' : [parameters[0]],
            'regParam' : [parameters[1]],
            'family': [parameters[2]],
            'link': [parameters[3]]
        }
    elif (model_name == RF):
        params = {
            'numTrees' : [parameters[0]],
            'maxDepth' : [parameters[1]],
            'seed' : [parameters[2]]
            }
    elif (model_name == GBTR):
        params = {
            'maxIter' : [parameters[0]],
            'maxDepth' : [parameters[1]],
            'stepSize': [parameters[2]],
            'seed' : [parameters[3]]
        }
        
    return params

###################
# --- COMMONS --- #
###################

'''
Description: Display the dataset information
Args:
    dataset: Dataset to show
Return: None
'''
def dataset_info(dataset):
  # Print dataset
  dataset.show(20)

  # Get the number of rows
  num_rows = dataset.count()

  # Get the number of columns
  num_columns = len(dataset.columns)

  # Print the shape of the dataset
  print("Shape:", (num_rows, num_columns))

  # Print the schema of the dataset
  dataset.printSchema()

'''
Description: Return the dataset with the selected features
Args:
    dataset: The dataset from which to extract the features
    features_normalization: Indicates whether features should be normalized (True) or not (False)
    features: list of features to be extracted
    features_label: The column name of features
    target_label: The column name of target variable
Return: 
    dataset: Dataset with the selected features
'''
def select_features(dataset, features_normalization, features, features_label, target_label):
    if features_normalization:
        # Assemble the columns into a vector column
        assembler = VectorAssembler(inputCols = features, outputCol = "raw_features")
        df_vector  = assembler.transform(dataset).select("timestamp", "id", "market-price", "raw_features", target_label)

        # Create a Normalizer instance using L2 norm
        normalizer = Normalizer(inputCol="raw_features", outputCol=features_label, p=2.0)

        # Fit and transform the data
        dataset = normalizer.transform(df_vector).select("timestamp", "id", "market-price", features_label, target_label)
    else:
        # Assemble the columns into a vector column
        assembler = VectorAssembler(inputCols = features, outputCol = features_label)
        dataset = assembler.transform(dataset).select("timestamp", "id", "market-price", features_label, target_label)

    return dataset

'''
Description: Plot the results obtained
Args:
    results: Results to be displayed
    title: Chart title
Return: None
'''
def show_results(dataset, train, valid, title, onlyTrain):
    if not onlyTrain:     
        trace1 = go.Scatter(
            x = dataset['timestamp'],
            y = dataset['next-market-price'].astype(float),
            mode = 'lines',
            name = 'Next Market price (usd)'
        )

        trace2 = go.Scatter(
            x = train['timestamp'],
            y = train['prediction'].astype(float),
            mode = 'lines',
            name = '(Train) Predicted next makert price (usd)'
        )

        trace3 = go.Scatter(
            x = valid['timestamp'],
            y = valid['prediction'].astype(float),
            mode = 'lines',
            name = '(Valid) Next Market price (usd)'
        )
    else:
        trace1 = go.Scatter(
            x = train['timestamp'],
            y = train['next-market-price'].astype(float),
            mode = 'lines',
            name = 'Next Market price (usd)'
        )

        trace2 = go.Scatter(
            x = train['timestamp'],
            y = train['prediction'].astype(float),
            mode = 'lines',
            name = 'Predicted next makert price (usd)'
        )
        
    layout = go.Layout(
        title=title,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    # Change the count to desired amount of months.
                    dict(count=1,
                        label='1m',
                        step='month',
                        stepmode='backward'),
                    dict(count=6,
                        label='6m',
                        step='month',
                        stepmode='backward'),
                    dict(count=12,
                        label='1y',
                        step='month',
                        stepmode='backward'),
                    dict(count=36,
                        label='3y',
                        step='month',
                        stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible = True
            ),
            type='date'
        )
    )

    if not onlyTrain:     
        data = [trace1,trace2,trace3]
    else:
        data = [trace1,trace2]

    fig = go.Figure(data=data, layout=layout)
    fig.show()   

'''
Description: Returns the average of the results obtained
Args:
    results: Obtained results from the model
    model_info: The model information to show
    evaluator_lst: The evaluator metrics to show
Return:
    comparison_df: Average of the results in a Pandas dataframe
'''
def model_comparison(results, model_info, evaluator_lst):
    # Calculate mean of all results
    col_mean_df = results[evaluator_lst].mean().to_frame().T

    # Extract model info
    model_info_df = results[model_info][:1]

    # Concatenate by row
    comparison_df = pd.concat([model_info_df, col_mean_df], axis=1)
    
    return comparison_df

'''
Description: Return the intialized model
Args:
    model_name: Model to be selected
    param: Parameters of the selected model
    features_label: The column name of features
    target_label: The column name of target variable
Return:
    model: Initialized model
'''
def model_selection(model_name, param, features_label, target_label):
    if model_name == LR:
        model = LinearRegression(featuresCol=features_label, \
                                    labelCol=target_label, \
                                    maxIter=param['maxIter'], \
                                    regParam=param['regParam'], \
                                    elasticNetParam=param['elasticNetParam'])
        
    elif model_name == GLR:
        model = GeneralizedLinearRegression(featuresCol=features_label, \
                                            labelCol=target_label, \
                                            maxIter=param['maxIter'], \
                                            regParam=param['regParam'])

    elif model_name == RF:
        model = RandomForestRegressor(featuresCol=features_label, \
                                        labelCol=target_label, \
                                        numTrees = param["numTrees"], \
                                        maxDepth = param["maxDepth"], \
                                        seed=param['seed'])

    elif model_name == GBTR:
        model = GBTRegressor(featuresCol=features_label, \
                                labelCol=target_label, \
                                maxIter = param['maxIter'], \
                                maxDepth = param['maxDepth'], \
                                stepSize = param['stepSize'], \
                                seed=param['seed'])

    return model

'''
Description: Return the metrics of the selected model
Args:
    target_label: The column name of target variable
    predictions: predictions made by the model
Return:
    results: Metrics obtained from the evaluation
'''
def model_evaluation(target_label, predictions):
    mse_evaluator = RegressionEvaluator(labelCol=target_label, predictionCol="prediction", metricName='mse')
    rmse_evaluator = RegressionEvaluator(labelCol=target_label, predictionCol="prediction", metricName='rmse')
    mae_evaluator = RegressionEvaluator(labelCol=target_label, predictionCol="prediction", metricName='mae')
    r2_evaluator = RegressionEvaluator(labelCol=target_label, predictionCol="prediction", metricName='r2')

    mape = mean_absolute_percentage_error(predictions.toPandas()[target_label], predictions.toPandas()["prediction"])

    mse = mse_evaluator.evaluate(predictions)
    rmse = rmse_evaluator.evaluate(predictions)
    mae = mae_evaluator.evaluate(predictions)
    r2 = r2_evaluator.evaluate(predictions)

    # Adjusted R-squared
    n = predictions.count()
    p = len(predictions.columns)
    adj_r2 = 1-(1-r2)*(n-1)/(n-p-1)

    results = {'rmse':rmse, 'mse':mse, 'mae':mae, 'mape':mape, 'r2':r2, 'adj_r2':adj_r2}

    return results

'''
Description: Return the accuracy of the model (how good the models are at predicting whether the price will go up or down)
Args:
    predictions: Predictions made by the model
Return: 
    accuracy: Percentage of correct predictions
'''
def model_accuracy(predictions):    
    # Compute the number of total rows in the DataFrame.
    total_rows = predictions.count()

    # Create a column "correct_prediction" which is worth 1 if the prediction is correct, otherwise 0
    predictions = predictions.withColumn(
        "correct_prediction",
        (
            (col("market-price") < col("next-market-price")) & (col("market-price") < col("prediction"))
        ) | (
            (col("market-price") > col("next-market-price")) & (col("market-price") > col("prediction"))
        )
    )

    # Count the number of correct predictions
    correct_predictions = predictions.filter(col("correct_prediction")).count()

    # Compite percentage of correct predictions
    accuracy = (correct_predictions / total_rows) * 100
        
    return accuracy

###########################
# --- MULTIPLE SPLITS --- #
###########################

'''
Description: Return the sets of split positions for block splits time series split
Args:
    num: Number of samples in the dataset
    n_splits: Split times
Return: 
    split_position_df: All sets of split positions in a Pandas dataset
'''
def block_splits(num, n_splits):
    # Calculate the split position for each fold 
    kfold_size = num // n_splits
    split_position_lst = []
    for i in range(n_splits):
        # Calculate the start/split/end point for each fold
        start = i * kfold_size
        end = start + kfold_size

        # Manually set train-validation split proportion in each fold
        split = int(0.8 * (end - start)) + start
        split_position_lst.append((start, split,end))
        
    # Transform the split position list to a Pandas dataset
    split_position_df = pd.DataFrame(split_position_lst, columns=['start', 'split', 'end'])

    return split_position_df

'''
Description: Return the sets of split positions for walk forward time series split
Args:
    num: Number of samples in the dataset
    min_obser: Minimum number of observations
    sliding_window: Sliding window size
Return: 
    split_position_df: All sets of split positions in a Pandas dataset
''' 
def walk_forward_splits(num, min_obser, sliding_window):
    # Calculate the split position for each fold 
    split_positions = []
    start = 0
    while start + min_obser + sliding_window <= num:
        split_positions.append((start, start + min_obser, start + min_obser + sliding_window))
        start += sliding_window

    # Transform the split position list to a Pandas dataset
    split_position_df = pd.DataFrame(split_positions, columns=['start', 'split', 'end'])

    return split_position_df

'''
Description: Perform train / validation using multiple splitting methods
Args:
    dataset: The dataset which needs to be splited
    params: Model's parameters to use
    splitting_info: Splitting method selected [block_splits | walk_forward_splits]
    model_name: Name of the model selected
    model_type: Model type [default | default_norm | cross_val | hyp_tuning]
    features_normalization: Indicates whether features should be normalized or not
    features: Features to be used to make predictions
    features_name: Name of features used
    features_label: The column name of features
    target_label: The column name of target variable
Return: 
    train_results_df: All the train splits performances in a pandas dataset
    valid_results_df: All the validations splits performances in a pandas dataset
    train_predictions_df: All the train splits predictions in a pandas dataset
    valid_predictions_df: All the validations splits predictions in a pandas dataset
'''
def multiple_splits(dataset, params, splitting_info, model_name, model_type, features_normalization, features, features_name, features_label, target_label, slow_operations):
    # Select the type of features to be used
    dataset = select_features(dataset, features_normalization, features, features_label, target_label)

    # Shows whether features are normalised or not
    if features_normalization:
        new_features_name = features_name + "_norm"
        features_name = new_features_name

    # Get the number of samples
    num = dataset.count()

    # Save results in a list
    all_train_results = []
    all_valid_results = []
    best_split_result = []

    # Initialize an empty list to store predictions
    all_train_predictions = []  
    all_valid_predictions = [] 

    # Identify the splitting type
    if splitting_info['split_type'] == BS:
        split_position_df = block_splits(num, splitting_info['splits'])
    elif splitting_info['split_type'] == WFS:
        split_position_df = walk_forward_splits(num, splitting_info['min_obser'], splitting_info['sliding_window'])
    num_splits = split_position_df.shape[0]

    for position in split_position_df.itertuples():
        best_result = {"RMSE": float('inf')}

        # Get the start/split/end position based on the splitting type
        start = getattr(position, 'start')
        splits = getattr(position, 'split')
        end = getattr(position, 'end')
        idx  = getattr(position, 'Index')
        
        # Train / validation size
        train_size = splits - start
        valid_size = end - splits

        # Get training data and validation data
        train_data = dataset.filter(dataset['id'].between(start, splits-1))
        valid_data = dataset.filter(dataset['id'].between(splits, end-1))

        # Cache them
        train_data.cache()
        valid_data.cache()
        
        # All combination of params
        param_lst = [dict(zip(params, param)) for param in product(*params.values())]

        for param in tqdm(param_lst):
            # Chosen Model
            model = model_selection(model_name, param, features_label, target_label)

            # Chain assembler and model in a Pipeline
            pipeline = Pipeline(stages=[model])

            # Train a model and calculate running time
            start = time.time()
            pipeline_model = pipeline.fit(train_data)
            end = time.time()

            # Make predictions
            train_predictions = pipeline_model.transform(train_data).select(target_label, "market-price", "prediction", 'timestamp')
            valid_predictions = pipeline_model.transform(valid_data).select(target_label, "market-price", "prediction", 'timestamp')

            # Show plots
            if slow_operations:
                if (model_type != "hyp_tuning"):
                    title = model_name + " predictions on split " +  str(idx + 1) + " with " + features_name
                    if splitting_info['split_type'] == BS: # Show all the plots (for BS)
                        show_results(dataset.toPandas(), train_predictions.toPandas(), valid_predictions.toPandas(), title, False)    
                    elif splitting_info['split_type'] == WFS: # Show only the first, the middle and the last split
                        if idx+1 == num_splits//2 or idx+1 == (num_splits//2) + 1: # Show only the middle plots (for WFS), uncomment this to show all of them (WARNING: you cannot save the notebook due to it's size)
                            show_results(dataset.toPandas(), train_predictions.toPandas(), valid_predictions.toPandas(), title, False)  
                    print("Split [" + str(idx + 1) + "/" + str(num_splits) +  "]")

            if model_type == "default" or model_type == "default_norm" or model_type == "cross_val":
                # Append predictions to the list
                all_train_predictions.append(train_predictions) 
                all_valid_predictions.append(valid_predictions)

            # Compute validation error by several evaluators
            train_eval_res = model_evaluation(target_label, train_predictions)
            valid_eval_res = model_evaluation(target_label, valid_predictions)

            # Use dict to store each result
            train_results = {
                "Model": model_name,
                "Type": model_type,
                "Dataset": 'train',
                "Splitting": splitting_info['split_type'],
                "Features": features_name,
                "Splits": idx + 1,
                "Train / Validation": (train_size,valid_size),                
                "Parameters": list(param.values()),
                "RMSE": train_eval_res['rmse'],
                "MSE": train_eval_res['mse'],
                "MAE": train_eval_res['mae'],
                "MAPE": train_eval_res['mape'],
                "R2": train_eval_res['r2'],
                "Adjusted_R2": train_eval_res['adj_r2'],
                "Time": end - start,
            }

            valid_results = {
                "Model": model_name,
                "Type": model_type,
                "Dataset": 'valid',
                "Splitting": splitting_info['split_type'],
                "Features": features_name,
                "Splits": idx + 1,
                "Train / Validation": (train_size,valid_size),                
                "Parameters": list(param.values()),
                "RMSE": valid_eval_res['rmse'],
                "MSE": valid_eval_res['mse'],
                "MAE": valid_eval_res['mae'],
                "MAPE": valid_eval_res['mape'],
                "R2": valid_eval_res['r2'],
                "Adjusted_R2": valid_eval_res['adj_r2'],
                "Time": end - start,
            }

            if model_type == "hyp_tuning":
                # Store the result with the lowest RMSE and the associated parameters
                if valid_results['RMSE'] < best_result['RMSE']:
                    best_result = valid_results

            if model_type == "default" or model_type == "default_norm" or model_type == "cross_val":
                # Store results for each split
                all_train_results.append(train_results)
                all_valid_results.append(valid_results)
        
        # Release Cache
        train_data.unpersist()
        valid_data.unpersist()

        if model_type == "hyp_tuning":
            # Store the best result for each split
            best_split_result.append(best_result) 
            print("Best parameters chosen for split [" + str(idx + 1) + "/" + str(num_splits) +  "]: " + str(best_result["Parameters"]))

    if model_type == "hyp_tuning":
        # Transform dict to pandas dataset
        best_split_result_df = pd.DataFrame(best_split_result)

        return best_split_result_df
    
    if model_type == "default" or model_type == "default_norm" or model_type == "cross_val":
        # Transform dict to pandas dataset
        all_train_results_df = pd.DataFrame(all_train_results)
        all_valid_results_df = pd.DataFrame(all_valid_results)

        # Iterate for each train and validation predictions and concatenate it with the final one
        all_train_predictions_df = pd.DataFrame()
        for pred in all_train_predictions:
            all_train_predictions_df = pd.concat([all_train_predictions_df, pred.select("*").toPandas()], ignore_index=True)

        all_valid_predictions_df = pd.DataFrame()
        for pred in all_valid_predictions:
            all_valid_predictions_df = pd.concat([all_valid_predictions_df, pred.select("*").toPandas()], ignore_index=True)

        return all_train_results_df, all_valid_results_df, all_train_predictions_df, all_valid_predictions_df

########################
# --- SINGLE SPLIT --- #
########################

'''
Description: Return the dataset ready to perform short term time series split
Args:
    dataset: The dataset which needs to be splited
    label: Type of splitting [weeks | months | years]
    proportion: A number represents the split proportion
Return: 
    train_data: The train dataset
    valid_data: The valid dataset
'''
def short_term_split(dataset, split_label, split_value):
    # Retrieve the last timestamp value
    last_value = dataset.agg(last("timestamp")).collect()[0][0]

    # Subtract the value from the last timestamp based on the split label
    match split_label:
        case "weeks":
            split_date = last_value - relativedelta(weeks=split_value)
        case "months":
            split_date = last_value - relativedelta(months=split_value)
        case "years":
            split_date = last_value - relativedelta(years=split_value)
        case _:
            return 

    # Split the dataset based on the desired date
    train_data = dataset[dataset['timestamp'] <= split_date]
    test_df = dataset[dataset['timestamp'] > split_date]

    return train_data, test_df

'''
Description: Perform train / validation using single split method
Args:
    dataset: The dataset which needs to be splited
    params: Model's parameters to use
    splitting_info: The splitting type method [short_term_split]
    model_name: Name of the model selected
    model_type: Model type [single_split]
    features_normalization: Indicates whether features should be normalized or not
    features: Features to be used to make predictions
    features_name: Name of features used
    features_label: The column name of features
    target_label: The column name of target variable
Return: 
    train_results_df: All the train splits performances in a pandas dataset
    valid_results_df: All the validations splits performances in a pandas dataset
    train_predictions_df: All the train splits predictions in a pandas dataset
    valid_predictions_df: All the validations splits predictions in a pandas dataset
'''
def single_split(dataset, params, splitting_info, model_name, model_type, features_normalization, features, features_name, features_label, target_label, slow_operations):
    # Select the type of features to be used
    dataset = select_features(dataset, features_normalization, features, features_label, target_label)

    # Shows whether features are normalised or not
    if features_normalization:
        new_features_name = features_name + "_norm"
        features_name = new_features_name

    # Get the number of samples
    num = dataset.count()

    # Get training data and validation data
    train_data, valid_data = short_term_split(dataset, splitting_info['split_label'], splitting_info['split_value'])
    
    # Train / validation size
    train_size = train_data.count()
    valid_size = valid_data.count()

    # Cache them
    train_data.cache()
    valid_data.cache()
    
    # All combination of params
    param_lst = [dict(zip(params, param)) for param in product(*params.values())]

    for param in param_lst:
        best_result = {"RMSE": float('inf')}

        # Chosen Model
        model = model_selection(model_name, param, features_label, target_label)

        # Chain assembler and model in a Pipeline
        pipeline = Pipeline(stages=[model])

        # Train a model and calculate running time
        start = time.time()
        pipeline_model = pipeline.fit(train_data)
        end = time.time()

        # Make predictions
        train_predictions = pipeline_model.transform(train_data).select(target_label, "market-price", "prediction", 'timestamp')
        valid_predictions = pipeline_model.transform(valid_data).select(target_label, "market-price", "prediction", 'timestamp')
        
        # Show plots
        title = model_name + " predictions with " + features_name
        if slow_operations:
            show_results(dataset.toPandas(), train_predictions.toPandas(), valid_predictions.toPandas(), title, False)

        # Compute validation error by several evaluators
        train_eval_res = model_evaluation(target_label, train_predictions)
        valid_eval_res = model_evaluation(target_label, valid_predictions)

        # Use dict to store each result
        train_results = {
            "Model": model_name,
            "Type": model_type,
            "Dataset": 'train',
            "Splitting": splitting_info['split_type'],
            "Features": features_name,
            "Train / Validation": (train_size,valid_size),                
            "Parameters": list(param.values()),
            "RMSE": train_eval_res['rmse'],
            "MSE": train_eval_res['mse'],
            "MAE": train_eval_res['mae'],
            "MAPE": train_eval_res['mape'],
            "R2": train_eval_res['r2'],
            "Adjusted_R2": train_eval_res['adj_r2'],
            "Time": end - start,
        }

        valid_results = {
            "Model": model_name,
            "Type": model_type,
            "Dataset": 'valid',
            "Splitting": splitting_info['split_type'],
            "Features": features_name,
            "Train / Validation": (train_size,valid_size),                
            "Parameters": list(param.values()),
            "RMSE": valid_eval_res['rmse'],
            "MSE": valid_eval_res['mse'],
            "MAE": valid_eval_res['mae'],
            "MAPE": valid_eval_res['mape'],
            "R2": valid_eval_res['r2'],
            "Adjusted_R2": valid_eval_res['adj_r2'],
            "Time": end - start,
        }
        
    # Release Cache
    train_data.unpersist()
    valid_data.unpersist()

    # Store train and validation results into pandas dataset
    train_results_df = pd.DataFrame.from_dict(train_results, orient='index').T
    valid_results_df = pd.DataFrame.from_dict(valid_results, orient='index').T

    return train_results_df, valid_results_df, train_predictions.toPandas(), valid_predictions.toPandas()
        
'''
Description: Evaluation of the final trained model
Args:
    dataset: The whole train / validation set
    params: Model's parameters to use
    model_name: Name of the model selected
    model_type: Model type [final]
    features_normalization: Indicates whether features should be normalized or not
    features: Features to be used to make predictions
    features_name: Name of features used
    features_label: The column name of features
    target_label: The column name of target variable
Return: 
    results_df: Results obtained from the evaluation
    pipeline_model: Final trained model
    predictions: Predictions obtained from the model
'''
def evaluate_trained_model(dataset, params, model_name, model_type, features_normalization, features, features_name, features_label, target_label):    
    # Select the type of features to be used
    dataset = select_features(dataset, features_normalization, features, features_label, target_label)

    # Shows whether features are normalised or not
    if features_normalization:
        new_features_name = features_name + "_norm"
        features_name = new_features_name
  
    # All combination of params
    param_lst = [dict(zip(params, param)) for param in product(*params.values())]
    
    for param in param_lst:
        # Chosen Model
        model = model_selection(model_name, param, features_label, target_label)
        
        # Chain assembler and model in a Pipeline
        pipeline = Pipeline(stages=[model])

        # Train a model and calculate running time
        start = time.time()
        pipeline_model = pipeline.fit(dataset)
        end = time.time()

        # Make predictions
        predictions = pipeline_model.transform(dataset).select(target_label, "market-price", "prediction", 'timestamp')

        # Compute validation error by several evaluators
        eval_res = model_evaluation(target_label, predictions)

        #  Use dict to store each result
        results = {
            "Model": model_name,
            "Type": model_type,
            "Dataset": 'train',
            "Splitting": "whole_train_valid",
            "Features": features_name,   
            "Parameters": [list(param.values())],
            "RMSE": eval_res['rmse'],
            "MSE": eval_res['mse'],
            "MAE": eval_res['mae'],
            "MAPE": eval_res['mape'],
            "R2": eval_res['r2'],
            "Adjusted_R2": eval_res['adj_r2'],
            "Time": end - start,
        }

    # Transform dict to pandas dataset
    results_df = pd.DataFrame(results)

    # Show plots
    show_results(None, predictions.toPandas(), None, model_name + " prediction on the whole train / validation set", True)
        
    return results_df, pipeline_model, predictions.toPandas()