"Test the actual and approximate moments of chi"

from scipy.stats import chi

if __name__ == '__main__':

	general_sigma = 0.1  # this gets divided by sqrt(df) to get scale per share

	df = 20
	scale = general_sigma / df ** 0.5
	print('Moments of chi with df= ', df)
	print('Moments of chi',chi.stats(df=df, scale=scale, moments='mvsk'))
	print('Approximate moments', general_sigma, scale * scale * (df - (df - 0.5)), (general_sigma ** 2) / (2 * df))
	
	print()
	df = 200
	print('Moments of chi with df= ', df)
	scale = general_sigma / df ** 0.5
	print('Moments of chi', chi.stats(df=df, scale=scale, moments='mvsk'))
	print('Approximate moments', general_sigma, scale * scale * (df - (df - 0.5)), (general_sigma ** 2) / (2 * df))
	
	# check scaling
	print(chi.pdf(x=0.1,df=df, scale=scale), chi.pdf(x=0.1/scale,df=df)/scale)
	