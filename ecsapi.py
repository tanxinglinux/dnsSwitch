# -*- coding:utf-8 -*-
__author__ = 'TanXing'

import json
import pprint
import aliyunsdkecs
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest,DescribeDisksRequest,DescribeRegionsRequest,DescribeInstanceRamRoleRequest,ModifyInstanceAttributeRequest
client = AcsClient('xxx','xxx','cn-shenzhen')

req = DescribeInstancesRequest.DescribeInstancesRequest()
# req1 = DescribeDisksRequest.DescribeDisksRequest()
# req2 = DescribeRegionsRequest.DescribeRegionsRequest()
req3 = DescribeInstanceRamRoleRequest.DescribeInstanceRamRoleRequest()
req4 = ModifyInstanceAttributeRequest.ModifyInstanceAttributeRequest()

req.set_accept_format('json')
# req1.set_accept_format('json')
# req2.set_accept_format('json')
req4.set_accept_format('json')
req4.set_InstanceId(['i-wz9fi442uvllfddenyxx'])
req4.set_InstanceName('worldpress')
print req4.get_InstanceName()
req3.set_accept_format('json')
req3.set_InstanceIds(['i-wz9fi442uvllfddenyxx'])

# print req3
# print req3.get_InstanceIds()

result = json.loads(client.do_action_with_exception(req)).get('Instances').get('Instance')[0]
# result1 = json.loads(client.do_action_with_exception(req1)).get('Disks').get('Disk')
# result2 = json.loads(client.do_action_with_exception(req2)).get('Regions').get('Region')
result3 = json.loads(client.do_action_with_exception(req3))


print result3


pprint.pprint(result)
# print len(result)
