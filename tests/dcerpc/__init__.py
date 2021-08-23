#!/usr/bin/env python
# Impacket - Collection of Python classes for working with network protocols.
#
# SECUREAUTH LABS. Copyright (C) 2021 SecureAuth Corporation. All rights reserved.
#
# This software is provided under a slightly modified version
# of the Apache Software License. See the accompanying LICENSE file
# for more information.
#
# Description:
#   Base class for testing DCE/RPC Endpoints.
#
# Author:
#   @martingalloar
#
from tests import RemoteTestCase

from impacket.dcerpc.v5 import transport, epm


class DCERPCTests(RemoteTestCase):

    STRING_BINDING_FORMATTING = 1
    STRING_BINDING_MAPPER = 2

    timeout = None
    authn = False
    authn_level = None
    iface_uuid = None
    protocol = None
    string_binding = None
    string_binding_formatting = STRING_BINDING_FORMATTING
    transfer_syntax = None
    machine_account = False

    def connect(self):
        """Obtains a RPC Transport and a DCE interface according to the bindings and
        transfer syntax specified.

        :return: tuple of DCE/RPC and RPC Transport objects
        :rtype: (DCERPC_v5, DCERPCTransport)
        """
        if not self.string_binding:
            raise NotImplemented("String binding must be defined")

        rpc_transport = transport.DCERPCTransportFactory(self.string_binding)

        # Set timeout if defined
        if self.timeout:
            rpc_transport.set_connect_timeout(self.timeout)

        # Authenticate if specified
        if self.authn and hasattr(rpc_transport, 'set_credentials'):
            # This method exists only for selected protocol sequences.
            rpc_transport.set_credentials(self.username, self.password, self.domain, self.lmhash, self.nthash)

        # Gets the DCE RPC object
        dce = rpc_transport.get_dce_rpc()

        # Set the authentication level
        if self.authn_level:
            dce.set_auth_level(self.authn_level)

        # Connect
        dce.connect()

        # Bind if specified
        if self.iface_uuid and self.transfer_syntax:
            dce.bind(self.iface_uuid, transfer_syntax=self.transfer_syntax)
        elif self.iface_uuid:
            dce.bind(self.iface_uuid)

        return dce, rpc_transport

    def setUp(self):
        super(DCERPCTests, self).setUp()
        self.set_transport_config(machine_account=self.machine_account)

        if self.string_binding_formatting == self.STRING_BINDING_FORMATTING:
            self.string_binding = self.string_binding.format(self)
        elif self.string_binding_formatting == self.STRING_BINDING_MAPPER:
            self.string_binding = epm.hept_map(self.machine, self.iface_uuid, protocol=self.protocol)
