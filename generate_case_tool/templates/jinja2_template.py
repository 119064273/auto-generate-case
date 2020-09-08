"""
Preconditions: {{ preconditions }}
------------------------------------
steps message:
{% set counter = 0 -%}
{% for step in steps -%}
({{ loop.index }}) {{ step }}
{% endfor -%}

------------------------------------
excepts result:
{% set counter = 0 -%}
{% for except in excepts -%}
({{ loop.index }}) {{ except }}
{% endfor -%}


NOTES NOTES:
There are {{ stepnum }} steps
# we searched two writed case similar to this case for you, please have a look: {{ pricase }}
"""
from case.CBaseCase import CBaseCase
from pub.Const import FAIL, PASS, INFO, BLOCK, DONE, ERROR


class {{ file_name }}(CBaseCase):
    """
     -------------------------------------------------------------------------------
     [Purpose ]:
     [Author  ]: {{ writer }}
     [Sprint  ]:
     [Tickets ]:
     [Platform]: {{ support_platform }}
     [Type    ]: auto
     [History ]:
     -------------------------------------------------------------------------------
    """

    def __init__(self):
        super({{ file_name }}, self).__init__(self.__class__.__name__)

    def config(self):
        """
        ************************************************
        [Purpose]:
        ************************************************
        """
        pass

    def func_step1(self, expected_resp):
        """
        ************************************************
        [Function]:
        [Input   ]:
        [Output  ]:
        ************************************************
        """
        # TODO

    def test(self):
        """
        ************************************************
        [Function]:
        [Input   ]:
        [Output  ]:
        ************************************************
        """
        {% set counter = 0 -%}
        {% for step in steps  -%}
        self.log("[{{ loop.index }}] {{ step }}")
        ret = func_step
        if not ret:
            self.result(FAIL, "ret={}".format(ret))

        {% endfor -%}

        pass

    def deconfig(self):
        """
        ************************************************
        [Purpose]:
        ************************************************
        """
        pass

