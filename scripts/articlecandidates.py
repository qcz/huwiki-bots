#!/usr/bin/python

import re
from string import Template
from datetime import datetime
from typing import List, Dict
import pywikibot
from pywikibot import date, pagegenerators

class ArticleCandidateBot:
    templatePage: str = u"Sablon:Cikkjelöltek"

    def run(self):
        site = pywikibot.Site()
        
        cjPage = pywikibot.Page(site, self.templatePage)
        cjPageText = cjPage.text

        articleCandidates = self.getArticleCandidates(site)
        existingTimestamps = self.getExistingArticleCandidateDatestamps(cjPageText)

        today = datetime.today().replace(hour=0, minute=0, second=0)

        freshArticles: List[str] = []
        twoWeekArticles: List[str] = []
        oneMonthArticles: List[str] = []

        for candidate in articleCandidates:
            timestamp = today
            if candidate in existingTimestamps:
                timestamp = existingTimestamps[candidate]
            else:
                existingTimestamps[candidate] = timestamp
            
            age = (today - timestamp).days
            if age < 14:
                freshArticles.append(candidate)
            elif age < 31:
                twoWeekArticles.append(candidate)
            else:
                oneMonthArticles.append(candidate)
        
        newPageText = re.sub(r"\|lista1=.*?\n", "|lista1=%s\n" % self.getArticleListForTemplatePage(freshArticles, existingTimestamps), cjPage.text)
        newPageText = re.sub(r"\|lista2=.*?\n", "|lista2=%s\n" % self.getArticleListForTemplatePage(twoWeekArticles, existingTimestamps), newPageText)
        newPageText = re.sub(r"\|lista3=.*?\n", "|lista3=%s\n" % self.getArticleListForTemplatePage(oneMonthArticles, existingTimestamps), newPageText)

        cjPage.text = newPageText
        cjPage.save(summary="Bot: Cikkjelöltek listájának frissítése")

    def getArticleListForTemplatePage(self, articleList: List[str], existingTimestamps: Dict[str, datetime.date]):
        ret = ""

        if len(articleList) > 0:
            ret = ", ".join(map(lambda x: Template("{{Cikkjelölt-hivatkozás|$article|$date}}").substitute(article=x, date=datetime.strftime(existingTimestamps[x], "%Y-%m-%d")), articleList))
        else:
            ret = "''nincs ilyen cikkjelölt''"
        
        return ret

    def getArticleCandidates(self, site: pywikibot.Site) -> List[str]:
        ret: List[str] = []

        category = pywikibot.Category(site, u"Kategória:Feljavításra váró cikkjelöltek")
        articles: List[pywikibot.Page] = category.members()
        for article in articles:
            articleTitle: str = article.title()
            if articleTitle.startswith(u"Wikipédia:Feljavításra váró cikkjelöltek/"):
                ret.append(articleTitle[41:])

        return ret

    def getExistingArticleCandidateDatestamps(self, cjPageText: str) -> Dict[str, datetime.date]:
        ret = {}

        pattern = re.compile(r"{{Cikkjelölt-hivatkozás\|(.*?)\|(\d{4}-\d{2}-\d{2})}}")
        matches = pattern.findall(cjPageText)
        for match in matches:
            try:
                dt = datetime.strptime(match[1], "%Y-%m-%d")
                ret[match[0]] = dt
            except ValueError:
                pass
        
        return ret

ArticleCandidateBot().run()
