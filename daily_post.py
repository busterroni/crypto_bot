import praw, datetime, time, requests, sys

########################
######## config ########
########################
username=""
password=""

#something to identify yourself to reddit (e.g. "bitcoin info updater v1.0 by /u/example")
useragent=""

#time to sleep in seconds after a network error:
time_to_sleep=0

#don't include the /r/ (e.g. just subreddit_to_post="example")
subreddit_to_post=""
########################
###### end config ######
########################

nl="\n\n"

def main(useragent, username, password):
	#login:
	r=praw.Reddit(useragent)
	login(username, password, r)

	#get current time:
	currTime=datetime.datetime.now()

	#create title and description:
	title=createTitleSkeleton(currTime)
	description=createDescriptionSkeleton(currTime)

	#add data to description:
	description+=getData()

	#attempt to submit post
	print "Attempting to submit post to /r/" + subreddit_to_post
	try:
		post=r.submit(subreddit_to_post, title=title, text=description)
	except praw.errors.APIException as e:
		if "SUBREDDIT_NOTALLOWED" in str(e):
			print "You do not have permission to post in /r/" + subreddit_to_post + ", exiting..."
		elif "SUBREDDIT_NOEXIST" in str(e):
			print "/r/" + subreddit_to_post + " does not exist, exiting..."
		else:
			print e
		sys.exit()
	print "Success! View at http://reddit.com/" + post.id

def login(username, password, r):
	#attempt to login
	connected=False
	while not connected:
		try:
			r.login(username, password)
			connected=True
			print "Logged in as " + username + "!"
		except requests.exceptions.ConnectionError:
			print "Could not log in, sleeping for " + str(time_to_sleep) + " seconds..."
			time.sleep(time_to_sleep)
		except praw.errors.InvalidUserPass:
			print "Error: Incorrect username or password."
			sys.exit()

def createTitleSkeleton(currTime):
	title="Bitcoin Network Status Update " + currTime.strftime('%A, %B %d, %Y')
	return title

def createDescriptionSkeleton(currTime):
	description="###Status of the Bitcoin network as of " + currTime.strftime('%A, %B %d, %Y') + " at " + currTime.strftime('%H:%M:%S') + " EST:"
	return description

def getData():
	print "Beginning to obtain network data..."
	description=nl

	#get and format data:
	bcStats=requests.get('https://api.smartbit.com.au/v1/blockchain/totals').json()['totals']
	block_count=int(bcStats['block_count'])
	totalBtc=float("%.8f" % float(bcStats['currency']))

	bcStatsDaily=requests.get('https://api.smartbit.com.au/v1/blockchain/stats').json()['stats']
	difficulty=float(bcStatsDaily['avg_difficulty'])

	blocks_day=int(bcStatsDaily['block_count'])
	outputs_day=float("%.8f" % float(bcStatsDaily['output_amount']))
	fees_day=float("%.8f" % float(bcStatsDaily['fees']))
	hashrate_day=float(bcStatsDaily['hash_rate_gh'])
	avg_blocktime_day=float(bcStatsDaily['block_interval_min'])

	avg_blocktime_day_secs=avg_blocktime_day-int(avg_blocktime_day)
	avg_blocktime_day_secs=str(int(avg_blocktime_day_secs*60))
	avg_blocktime_day=int(avg_blocktime_day)

	prices=requests.get('https://api.smartbit.com.au/v1/exchange-rates').json()['exchange_rates']
	priceUSD=float(prices[7]['rate'])

	#adding commas to data
	block_count=str("{:,}".format(block_count))
	totalBtc=str("{:,}".format(totalBtc))
	difficulty=str("{:,}".format(difficulty))

	blocks_day=str("{:,}".format(blocks_day))
	outputs_day=str("{:,}".format(outputs_day))
	fees_day=str("{:,}".format(fees_day))
	avg_blocktime_day=str("{:,}".format(avg_blocktime_day))
	hashrate_day=str("{:,}".format(hashrate_day))

	#one can only hope this is necessary...
	priceUSD=str("{:,}".format(priceUSD))


	#adding data to description:
	description+="**Total bitcoins:** " + totalBtc + nl
	description+="**Height:** " + block_count + nl
	description+="**Difficulty:** " + difficulty + nl

	description+="######Statistics for the past 24 hours:" + nl
	description+="**Number of blocks mined:** " + blocks_day + nl
	description+="**Total bitcoins output (amount sent):** " + outputs_day  + nl
	description+="**Total fees:** " + fees_day + nl
	description+="**Average time until block found:** " + avg_blocktime_day + " minutes, " + avg_blocktime_day_secs + " seconds" + nl
	description+="**Estimated hashrate:** " + hashrate_day + " gh/s" + nl
	description+="**Current price:** US$" + priceUSD + nl

	description+="*Data provided by [Smartbit.com.au](https://www.smartbit.com.au).*" + nl

	description+="***" + nl

	description+="^^I ^^am ^^a ^^bot. **[^^My ^^commands](http://www.reddit.com/r/Bitcoin/comments/3an2c4/ive_been_working_on_a_bot_for_crypto_subs_like/)** ^^| ^^*/r/crypto_bot* ^^| [^^Message ^^my ^^creator](http://www.reddit.com/message/compose?to=busterroni) ^^| [^^Source](https://github.com/busterroni/crypto_bot)"

	return description

if __name__=="__main__":
	main(useragent, username, password)
