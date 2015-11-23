#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_renderer
----------------------------------

Tests for `renderer` module.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import common
from wikipediabase import renderer
from wikipediabase.util import fromstring

infobox_source = """
{{Template:Infobox_officeholder
 | office = !!!!!office!!!!!
| serviceyears = !!!!!serviceyears!!!!!
| battles = !!!!!battles!!!!!
| Usage = !!!!!Usage!!!!!
| portfolio = !!!!!portfolio!!!!!
| alt = !!!!!alt!!!!!
| children = !!!!!children!!!!!
| succeeding = !!!!!succeeding!!!!!
| occupation = !!!!!occupation!!!!!
| style = !!!!!style!!!!!
| candidate = !!!!!candidate!!!!!
| also = !!!!!also!!!!!
| resting_place = !!!!!resting_place!!!!!
| infobox = !!!!!infobox!!!!!
| parents = !!!!!parents!!!!!
| ambassador_from = !!!!!ambassador_from!!!!!
| Judge = !!!!!Judge!!!!!
| birth_name = !!!!!birth_name!!!!!
| colwidth = !!!!!colwidth!!!!!
| predecessor = !!!!!predecessor!!!!!
| branch = !!!!!branch!!!!!
| Ambassador = !!!!!Ambassador!!!!!
| chancellor = !!!!!chancellor!!!!!
| party = !!!!!party!!!!!
| primeminister = !!!!!primeminister!!!!!
| successor = !!!!!successor!!!!!
| constituency_AM = !!!!!constituency_AM!!!!!
| Senators = !!!!!Senators!!!!!
| committees = !!!!!committees!!!!!
| name = !!!!!name!!!!!
| death_date = !!!!!death_date!!!!!
| Congressman = !!!!!Congressman!!!!!
| runningmate = !!!!!runningmate!!!!!
| templates = !!!!!templates!!!!!
| Representatives = !!!!!Representatives!!!!!
| module = !!!!!module!!!!!
| years_active = !!!!!years_active!!!!!
| assembly = !!!!!assembly!!!!!
| state_senate = !!!!!state_senate!!!!!
| constituency_MP = !!!!!constituency_MP!!!!!
| hidelinks = !!!!!hidelinks!!!!!
| smallimage = !!!!!smallimage!!!!!
| religion = !!!!!religion!!!!!
| state = !!!!!state!!!!!
| Representative = !!!!!Representative!!!!!
| alma_mater = !!!!!alma_mater!!!!!
| state_legislature = !!!!!state_legislature!!!!!
| resting_place_coordinates = !!!!!resting_place_coordinates!!!!!
| embed = !!!!!embed!!!!!
| lieutenant = !!!!!lieutenant!!!!!
| awards = !!!!!awards!!!!!
| Senator = !!!!!Senator!!!!!
| constituency = !!!!!constituency!!!!!
| commands = !!!!!commands!!!!!
| country = !!!!!country!!!!!
| vicepresident = !!!!!vicepresident!!!!!
| viceprimeminister = !!!!!viceprimeminister!!!!!
| caption = !!!!!caption!!!!!
| signature = !!!!!signature!!!!!
| footnotes = !!!!!footnotes!!!!!
| governor_general = !!!!!governor_general!!!!!
| honorific-suffix = !!!!!honorific-suffix!!!!!
| deputy = !!!!!deputy!!!!!
| image = !!!!!image!!!!!
| profession = !!!!!profession!!!!!
| allegiance = !!!!!allegiance!!!!!
| rank = !!!!!rank!!!!!
| Member = !!!!!Member!!!!!
| birth_place = !!!!!birth_place!!!!!
| nationality = !!!!!nationality!!!!!
| state_assembly = !!!!!state_assembly!!!!!
| unit = !!!!!unit!!!!!
| district = !!!!!district!!!!!
| nickname = !!!!!nickname!!!!!
| relations = !!!!!relations!!!!!
| term_end = !!!!!term_end!!!!!
| opponent = !!!!!opponent!!!!!
| website = !!!!!website!!!!!
| parliament = !!!!!parliament!!!!!
| death_place = !!!!!death_place!!!!!
| appointer = !!!!!appointer!!!!!
| Microformat = !!!!!Microformat!!!!!
| cabinet = !!!!!cabinet!!!!!
| term_start = !!!!!term_start!!!!!
| image_size = !!!!!image_size!!!!!
| appointed = !!!!!appointed!!!!!
| signature_alt = !!!!!signature_alt!!!!!
| governor = !!!!!governor!!!!!
| state_house = !!!!!state_house!!!!!
| limit = !!!!!limit!!!!!
| residence = !!!!!residence!!!!!
| nominator = !!!!!nominator!!!!!
| known_for = !!!!!known_for!!!!!
| citizenship = !!!!!citizenship!!!!!
| nominee = !!!!!nominee!!!!!
| taoiseach = !!!!!taoiseach!!!!!
| alongside = !!!!!alongside!!!!!
| party_election = !!!!!party_election!!!!!
| native_name = !!!!!native_name!!!!!
| hidetrans = !!!!!hidetrans!!!!!
| partner = !!!!!partner!!!!!
| education = !!!!!education!!!!!
| Parliament = !!!!!Parliament!!!!!
| prior_term = !!!!!prior_term!!!!!
| namespace = !!!!!namespace!!!!!
| mawards = !!!!!mawards!!!!!
| majority = !!!!!majority!!!!!
| speaker = !!!!!speaker!!!!!
| incumbent = !!!!!incumbent!!!!!
| monarch = !!!!!monarch!!!!!
| native_name_lang = !!!!!native_name_lang!!!!!
| otherparty = !!!!!otherparty!!!!!
| election_date = !!!!!election_date!!!!!
| state_delegate = !!!!!state_delegate!!!!!
| Governor = !!!!!Governor!!!!!
| president = !!!!!president!!!!!
| honorific-prefix = !!!!!honorific-prefix!!!!!
| spouse = !!!!!spouse!!!!!
| data = !!!!!data!!!!!
| class = !!!!!class!!!!!
| TemplateData = !!!!!TemplateData!!!!!
| sr = !!!!!sr!!!!!
| birth_date = !!!!!birth_date!!!!!
| order = !!!!!order!!!!!
}}
"""

class TestRenderer(unittest.TestCase):

    def setUp(self):
        #self.rndr = renderer.SandboxRenderer(configuration=common.testcfg)
        self.rndr = renderer.ApiRenderer(configuration=common.testcfg)

    def test_infobox(self):
        html_str = self.rndr.render(infobox_source)
        self.assertIn("!order!", html_str)

    def test_render(self):
        render_text = "Bawls of steed"
        html_str = self.rndr.render(render_text)
        # If this fails it is possible that wikipedia.org has blocked
        # you. Use a mirror.
        self.assertNotIn("wpTextbox1", html_str, "Get just the contents..")
        self.assertIn(render_text, html_str, "Body not found")

    def test_render_ibox(self):
        ibx_txt ="""{{Infobox person
| name =  Sam Dunn
| birth_date = {{birth date and age|1974|3|20|df=y}}
| birth_place = [[Stroud]], [[England]]
}}"""
        self.assertIn("March 1974", self.rndr.render(ibx_txt))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
