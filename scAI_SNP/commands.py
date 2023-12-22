import sys
import typer
import numpy as np
import pandas as pd
import cvxpy as cp
import time

from scAI_SNP.helper import (read_center, read_validate, center_scale_input, get_name_input, save_prob_plot,
							 ensure_directory_exists, n_mut, is_valid_path, ensure_trailing_slash)


app = typer.Typer(
	help = "Command line tool to extract genetic population classification of mutation data "
		"using HGDP project"
)

@app.command(short_help="classify the data")
def classify(file_input, path_output, name_input = None, bool_save_plot = True):
	now = time.time()
	print(f"starting ancestry classification for scAI-SNP")
	print(f"python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
	print(f"input file path: {file_input}")	

	# ensure the output directory exists and creates it if needed
	ensure_directory_exists(path_output)

	# read the input data
	mat_input = read_validate(file_input)
	
	# count the number of columns in the input
	n_sample = mat_input.shape[1]
	print(f"found {n_sample} inputs in the input file")

	# get the sample name
	vec_name_input = get_name_input(file_input, name_input, n_sample)

	# read the mean genotype of the training data
	col_mean = read_center()

	# centering the input data and count the number of missing values
	mat_input_centered_scaled, vec_n_missing = center_scale_input(mat_input, col_mean)

	print(f"input has {n_sample} samples (columns)")
	print(f"each sample is missing {np.around(vec_n_missing/n_mut * 100, 2)} % genotypes")
	print("SUCCESS: centering complete!")
	
 	## original
	# print("reading LDA projection matrix...")
	# mat_proj_lda = pd.read_csv('data/proj_lda.tsv.gz', sep = '\t', compression = 'gzip', header = None).values
	# print("SUCCESS: projection matrix loaded!")
	# print("applying classification...")
	
 	## new
	print("reading PCA projection matrix...")
	print(f"cp version: {cp.__version__}")
	# mat_proj_pca = pd.read_csv('data/proj_pca.tsv.gz', sep = '\t', compression = 'gzip', header = None).values
	mat_proj_pca = pd.read_csv(f'data/proj_PCA/mat_proj_PCA_cc1.tsv.gz', compression = 'gzip', sep = '\t', header = None).values
	print(f'shape of mat_proj_pca (4.5M by 100): {mat_proj_pca.shape}')
	print("SUCCESS: PCA projection matrix loaded!")

	
 	## original
	# lda_proj_input = mat_input_centered_scaled.T @ mat_proj_lda
	## new
 
	print("reading mean PCA matrix...")
	mat_mean_PC = pd.read_csv(f'data/mat_GT_PCA_projected_mean.tsv', sep = '\t', header = None).values
	mat_mean_PC = mat_mean_PC[0:100,:]	
	print(f'shape of mat_mean_P (100 by 26): {mat_mean_PC.shape}')
	print("SUCCESS: mean PCA matrix loaded!")
 
	
	print("applying PCA...")
	print(f'shape of mat_input_centered_scaled (4.5M by n_sample): {mat_input_centered_scaled.shape}')
	pca_projected_input = mat_input_centered_scaled.T @ mat_proj_pca
	print("SUCCESS: PCA applied!")
 
	## original
	# coef_lr = pd.read_csv('model/LR/LR_coef.tsv', sep = '\t', header = None).to_numpy()
	# intercept_lr = pd.read_csv('model/LR/LR_intercept.tsv', sep = '\t', header = None).to_numpy()
	# vec_population = pd.read_csv('model/LR/population.tsv', header = None).to_numpy().flatten()
	
	# scores = lda_proj_input @ coef_lr.T + intercept_lr.T
	
	# print(f"scores dimension: {scores.shape}")
	# index_max = np.argmax(scores, axis = 1)
	# prob = np.exp(scores) / np.sum(np.exp(scores), axis = 1, keepdims = True)

	#for sample in range(n_sample):
	#	print(f"For sample {sample + 1}:")
	#	print(f"classified population: {vec_population[index_max[sample]]}")
	#	print(f"prob: {prob[sample, index_max[sample]]}")
	## new
	# under construction
 
	def predict_convex(test_vec, mean_vectors = mat_mean_PC):
		# Define the optimization variable
		X = cp.Variable(26)
		# Define the objective function (minimize the least squares error)
		objective = cp.Minimize(cp.norm(mean_vectors @ X - test_vec, 'fro'))
		# Define the constraints
		constraints = [X >= 0, cp.sum(X) == 1]

		# Define and solve the problem
		problem = cp.Problem(objective, constraints)
		problem.solve()
		this_predicted = X.value

		# Use this_predicted to construct a prediction vector from the mean_vectors
		vec_predicted = mean_vectors @ this_predicted

		# Compute the cosine similarity between this_vector and test_vec
		cos_sim = np.dot(vec_predicted, test_vec) / (np.linalg.norm(vec_predicted) * np.linalg.norm(test_vec))  # cosine similarity is computed using this single line of code ***

		return this_predicted, cos_sim

	print("applying classification...")
	list_predicted = []
	list_angle = []
	for index_sample in range(n_sample):
		vec_prob, angle = predict_convex(pca_projected_input[index_sample,:].T)
		list_predicted.append(vec_prob)
		list_angle.append(angle)
	
	print("SUCCESS: classification done!")
	print(f"classify took {round((time.time() - now)/60, 2)} minutes")
	print("Saving probabilities...")

	if (n_sample == 1):
		prob = vec_prob.reshape(1, -1)
	else:
		prob = np.array(list_predicted)

	df_prob = pd.DataFrame(prob.T, index = vec_population, columns = vec_name_input)
	print(f"saving probabilities to output/probabilities.tsv")
	df_prob.to_csv(sep = '\t', path_or_buf = ensure_trailing_slash(path_output) + 'df_probabilities.tsv', index = True)
	print("SUCCESS: probabilities saved!")

	if (bool_save_plot):
		save_prob_plot(df_prob, vec_name_input, n_sample, path_output)
	return df_prob


def cmd_classify(args=None):
	import argparse
	parser = argparse.ArgumentParser(
		description = "Command line tool to extract genetic population classification of mutation data"
	)
	
	# required arguments
	parser.add_argument('file_input', help = "input genotype file path")
	parser.add_argument('path_output', help = "output genotype folder path")
	
	# optional arguments
	parser.add_argument('--name_input', default = None, help= "input sample names (file path) (default: None).")
	parser.add_argument('--bool_save_plot', type = bool, default = True, help = "Flag to save plot (default: True).")

	parsed_args = parser.parse_args(args)
	
	classify(parsed_args.file_input, parsed_args.path_output, parsed_args.name_input, parsed_args.bool_save_plot)