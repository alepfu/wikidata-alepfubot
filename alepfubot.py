#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
AlepfuBot adds the claim "drug action altered by" to drug items. Claims are 
imported via a CSV file of the following format: 
    "object-drug","DrugbankID","precipitant-drug","DrugbankID".

The following parameters are supported:

&params;

-dry              If set, nothing will be changed.

-file=<url>       Full HTTP url to file.

-delim=<char>     CSV delimiter character  


Example usage:

python alepfubot.py -file=http://www.example.com/data/file.csv -delim=$                
"""
#
# (C) Alexander Pfundner (Alepfu), 2014
#
# Distributed under the terms of the MIT license.
#

__version__ = '$Id$'

import pywikibot
from pywikibot import pagegenerators
import urllib
import csv

# This is required for the command line help
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}


class AlepfuBot:
    """
    Adds "drug action altered by" claims to drug items.
    """
    
    def __init__(self, isDry, csvFile, delim):
        """
        Constructor

        Parameters:     
            @param isDry: If set, nothing will be changed.                      
            @type isDry: boolean.
            @param csvFile: Http-Link to remote file.                      
            @type csvFile: unicode.
            @param delim: CSV delimiter character                      
            @type delim: unicode.
        """
        
        self.isDry = isDry
        self.csvFile = csvFile
        self.delim = delim

    def run(self):
        """ 
        Steps:
            1) Download CSV file
            2) Parse CSV file
            3) Some checks regarding correctness
            4) Add claims to wikidata
        """
        
        # Download CSV file
        print "Downloading file", self.csvFile
        fileName = self.csvFile[self.csvFile.rfind("/")+1:]
        urllib.urlretrieve(self.csvFile, fileName)
        print "File", fileName, "saved"
        
        # Init site, repository, claim and source       
        site = pywikibot.Site("en", "wikipedia")
        repo = site.data_repository()
        claim = pywikibot.Claim(repo, u'P769')
        statedIn = pywikibot.Claim(repo, u'P248')
        source = pywikibot.ItemPage(repo, "Q17505343")
        statedIn.setTarget(source)        
        
        # Open file       
        csvReader = csv.reader(open(fileName, "rb"), delimiter=self.delim.encode('utf-8'))  # delimiter needs to be str
        
        # Loop over all entries from the file        
        for row in csvReader:
            objDrug = row[0].decode("utf-8")      # because reader delivers str
            objDrugId = row[1].decode("utf-8")
            preDrug = row[2].decode("utf-8")
            preDrugId = row[3].decode("utf-8")
            print "Adding claim:", objDrug, objDrugId, preDrug, preDrugId
            
            # Remove prefix from DrugBank IDs
            if objDrugId.startswith("DB"):
                objDrugId = objDrugId[2:]            
            if preDrugId.startswith("DB"):
                preDrugId = preDrugId[2:]
            
            # Load the object and precipitant items, if an item is missing the entry will be skipped  
            objDrugPage = pywikibot.Page(site, objDrug)
            objDrugItem = pywikibot.ItemPage.fromPage(objDrugPage)
            if objDrugItem.exists():
                objDrugItem.get()
            else:
                print "No item found for", objDrug    
                print "Skipping entry"
                continue
            preDrugPage = pywikibot.Page(site, preDrug)
            preDrugItem = pywikibot.ItemPage.fromPage(preDrugPage)
            if preDrugItem.exists():
                preDrugItem.get()
            else:
                print "No item found for", preDrug    
                print "Skipping entry"
                continue
           
            # Check for correct DrugBank IDs
            print "Checking DrugBank IDs"
            if objDrugItem.claims:
                if "P715" in objDrugItem.claims:
                    if not objDrugItem.claims["P715"][0].getTarget() == objDrugId:
                        print "Object ID is incorrect"
                        print "Skipping entry"
                        continue                
            if preDrugItem.claims:
                if "P715" in preDrugItem.claims:
                    if not preDrugItem.claims["P715"][0].getTarget() == preDrugId:
                        print "Precipitant ID is incorrect"
                        print "Skipping entry"
                        continue            
            
            # Init the check flag, if this switches to false, the entry will be skipped
            isOk = True
                        
            # Check for existing claims
            print "Checking for existing claims"
            preLabel = preDrugItem.labels.get("en")
            if objDrugItem.claims:
                if "P769" in objDrugItem.claims:
                    precipitants = objDrugItem.claims["P769"]               
                    for p in precipitants:                     # TODO make more elegant
                        pitem = p.getTarget();
                        pitem.get();
                        label = pitem.labels.get("en")
                        if label == preLabel: 
                            isOk = False
                            print "Found entry for precipitant", label          

            # Skip entry if a check failed
            if isOk:
                print "Applying changes"
                if not self.isDry:
                    claim.setTarget(preDrugItem)    
                    objDrugItem.addClaim(claim)
                    claim.addSources([statedIn])
                else:
                    print "Bot is set dry"
            else:
                print "Skipping entry"    
       
            
 
def main():
    """
    Process command line arguments and invoke AlepfuBot.
    """
    
    # Init args variables
    isDry = False
    csvFile = None
    delim = None
    
    # Loop over the passed local args
    for arg in pywikibot.handleArgs():
        if arg.startswith("-dry"):
            isDry = True
        if arg.startswith("-file"):
            csvFile = arg[arg.find("=")+1:]
        if arg.startswith("-delim"):
            delim = arg[arg.find("=")+1:]    

    # Run the bot
    bot = AlepfuBot(isDry, csvFile, delim)
    bot.run()


if __name__ == "__main__":
    main()
