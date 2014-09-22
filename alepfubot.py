#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
AlepfuBot adds ...

The following parameters are supported:

&params;

-isDry              If given, doesn't do any real changes, but only logs
                  what would have been changed.
                  
                  

"""
#
# (C) Alexander Pfundner (Alepfu), 2014
#
# Distributed under the terms of the MIT license.
#

__version__ = '$Id$'

import pywikibot
from pywikibot import pagegenerators

# This is required for the command line help
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}


class AlepfuBot:
    """
    Adds the claim "drug action altered by".
    """
    
    def __init__(self, isDry):
        """
        Constructor

        Parameters:     
            @param isDry: todo.                       
            @type myparam: boolean.
        """
        self.isDry = isDry

    def run(self):
        """ 
        Steps:
            1) todo
        """
        
        # Init some test data
        drugs = [{"object":"Atomoxetine", "objectid":"DB00289", "precip":"Isocarboxazid", "precipid":"DB01247"},
                    {"object":"Atomoxetine", "objectid":"DB00289", "precip":"Phenelzine", "precipid":"DB00780"},
                    {"object":"Atomoxetine", "objectid":"DB00289", "precip":"Procarbazine", "precipid":"DB01168"},
                    {"object":"Atomoxetine", "objectid":"DB00289", "precip":"Selegiline", "precipid":"DB01037"},
                    {"object":"Atomoxetine", "objectid":"DB00289", "precip":"Tranylcypromine", "precipid":"DB00752"}]
        
        # Init site, repository, claim and source reference       
        site = pywikibot.Site("en", "wikipedia")
        repo = site.data_repository()
        claim = pywikibot.Claim(repo, u'P769')
        statedIn = pywikibot.Claim(repo, u'P248')
        source = pywikibot.ItemPage(repo, "Q17505343")
        statedIn.setTarget(source)        
        
        # Loop over all entries from the file
        for drug in drugs:
            objDrug = drug.get("object")
            preDrug = drug.get("precip")
            objDrugId = drug.get("objectid")
            preDrugId = drug.get("precipid")
            
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

            # Init the check flag, if this switches to false, the entry will be skipped
            isOk = True
            
            # Check for correct DrugBank IDs
            print "Checking DrugBank IDs"
            if objDrugItem.claims:
                if "P715" in objDrugItem.claims:
                    if not objDrugItem.claims["P715"][0].getTarget() == objDrugId:
                        isOK = False
                        print "Object ID is incorrect"                
            if preDrugItem.claims:
               if "P715" in preDrugItem.claims:
                   if not preDrugItem.claims["P715"][0].getTarget() == preDrugId:
                       isOK = False
                       print "Precipitant ID is incorrect"
            
            # Check for existing claims
            print "Checking for existing claims"
            preLabel = preDrugItem.labels.get("en")
            if objDrugItem.claims:
                if "P769" in objDrugItem.claims:
                    precipitants = objDrugItem.claims["P769"]               
                    for p in precipitants:
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
                    print "#### Bot is set dry ####"
            else:
                print "Skipping entry"    
       
            
 
def main():
    """
    Process command line arguments and invoke AlepfuBot.
    """
    
    # Init args variables
    isDry = False
    
    # Loop over the passed local args
    for arg in pywikibot.handleArgs():
        if arg.startswith("-dry"):
            isDry = True
 
    # Run the bot
    bot = AlepfuBot(isDry)
    bot.run()


if __name__ == "__main__":
    main()
