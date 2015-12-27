#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import shlex
from munin import MuninPlugin

spam_result_re = re.compile("(No|Yes), score=(-?\d+(?:\.\d+)?) tagged_above=(-?\d+(?:\.\d+)?) required=(-?\d+(?:\.\d+)?)")

class SpamassassinSpamHamScorePlugin(MuninPlugin):
	title = "Spamassassin Spam/Ham score"
	category = 'mail'
	vlabel = 'Score'
	scale = 'no'

	@property
	def fields(self):
		return (
			('avg_spam_score', { 'label': 'Average Spam score', 'type': 'GAUGE', 'info': 'Average spamassassin score for mails marked as Spam' }),
			('max_spam_score', { 'label': 'Maximum Spam score', 'type': 'GAUGE', 'info': 'Maximum score for a Spam mail' }),
			('min_spam_score', { 'label': 'Minimum Spam score', 'type': 'GAUGE', 'info': 'Minimum score for a Spam mail' }),

			('avg_ham_score', { 'label': 'Average ham score', 'type': 'GAUGE', 'info': 'Average spamassassin score for mails marked as ham' }),
			('max_ham_score', { 'label': 'Maximum Ham score', 'type': 'GAUGE', 'info': 'Maximum score for a Spam mail' }),
			('min_ham_score', { 'label': 'Minimum Ham score', 'type': 'GAUGE', 'info': 'Minimum score for a Spam mail' }),

			('required_score', { 'label': 'Required score', 'type': 'GAUGE', 'info': 'Required score to mark a mail as Spam' }),
			('tagged_above', { 'label': 'Tag score', 'type': 'GAUGE', 'info': 'Score required to tag a mail' }),
		)

	def execute(self):
		logfile = os.environ.get('logfile', '/var/log/mail.log')

		grep_proc = subprocess.Popen(shlex.split("grep 'spam-tag, ' %s" % logfile), stdout=subprocess.PIPE)
		stdout, _ = grep_proc.communicate()

		spam_scores = []
		ham_scores = []
		required = []
		tagged_above = []

		for line in stdout.splitlines():
			tests_m = spam_result_re.search(line)
			if not tests_m:
				continue
			is_spam, score, tag, req = tests_m.groups()
			if is_spam == 'No':
				ham_scores.append(float(score))
			else:
				spam_scores.append(float(score))
			required.append(float(req))
			tagged_above.append(float(tag))

		avg_spam_score = sum(spam_scores) / len(spam_scores) if spam_scores else 0.0
		avg_ham_score = sum(ham_scores) / len(ham_scores) if ham_scores else 0.0
		avg_required_score = sum(required) / len(required) if required else 0.0
		avg_tagged_above = sum(tagged_above) / len(tagged_above) if tagged_above else 0.0

		print("avg_spam_score.value %s" % avg_spam_score)
		print("max_spam_score.value %s" % (max(spam_scores) if spam_scores else "", ))
		print("min_spam_score.value %s" % (min(spam_scores) if spam_scores else "", ))

		print("avg_ham_score.value %s" % avg_ham_score)
		print("max_ham_score.value %s" % (max(ham_scores) if ham_scores else "", ))
		print("min_ham_score.value %s" % (min(ham_scores) if ham_scores else "", ))

		print("required_score.value %s" % avg_required_score)
		print("tagged_above.value %s" % avg_tagged_above)

if __name__ == '__main__':
	SpamassassinSpamHamScorePlugin().run()