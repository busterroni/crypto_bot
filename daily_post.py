import praw, datetime, time, requests, sys

########################
######## config ########
########################
username=""
password=""

#something to identify yourself to reddit (e.g. "bitcoin info updater v1.0 by /u/example")
useragent=""

#time to sleep in seconds after a network error:
time_to_sleep=60

subreddit_to_post=""
########################
###### end config ######
########################

nl="\n\n"

def main(useragent, username, password):
	#login:
	r = praw.Reddit(client_id='',
			client_secret='',
			username=username,
			password=password,
			user_agent=useragent)

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
		post=r.subreddit(subreddit_to_post).submit(title=title, selftext=description)
	except praw.exceptions.APIException as e:
		if "SUBREDDIT_NOTALLOWED" in str(e):
			print "You do not have permission to post in /r/" + subreddit_to_post + ", exiting..."
		elif "SUBREDDIT_NOEXIST" in str(e):
			print "/r/" + subreddit_to_post + " does not exist, exiting..."
		else:
			print e
		sys.exit()
	print "Success! View at https://reddit.com/" + post.id

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

	price=float(requests.get('https://api.coinbase.com/v2/prices/spot?currency=USD').json()['data']['amount'])

	#adding commas to data
	block_count=str("{:,d}".format(block_count))
	totalBtc=str("{:,f}".format(totalBtc))
	difficulty=str("{:,f}".format(difficulty))

	blocks_day=str("{:,d}".format(blocks_day))
	outputs_day=str("{:,f}".format(outputs_day))
	fees_day=str("{:,f}".format(fees_day))
	avg_blocktime_day=str("{:,d}".format(avg_blocktime_day))
	hashrate_day=str("{:,f}".format(hashrate_day))

	#one can only hope this is necessary...
	priceUSD=str("{:,.2f}".format(price))


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

	description+="^^I ^^am ^^a ^^bot. **[^^My ^^commands](https://www.reddit.com/r/Bitcoin/comments/3an2c4/ive_been_working_on_a_bot_for_crypto_subs_like/)** ^^| ^^*/r/crypto_bot* ^^| [^^Message ^^my ^^creator](https://www.reddit.com/message/compose?to=busterroni) ^^| [^^Source ^^code](https://github.com/busterroni/crypto_bot)"

	return description

if __name__=="__main__":
	main(useragent, username, password)
