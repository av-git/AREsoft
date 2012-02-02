# This file is part of Androguard.
#
# Copyright (C) 2011, Anthony Desnos <desnos at t0t0.fr>
# All rights reserved.
#
# Androguard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Androguard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of  
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Androguard.  If not, see <http://www.gnu.org/licenses/>.

from networkx import DiGraph
from xml.sax.saxutils import escape


import libsign
import bytecode
from dvm_permissions import DVM_PERMISSIONS
from risk import PERMISSIONS_RISK, INTERNET_RISK, PRIVACY_RISK, PHONE_RISK, SMS_RISK, MONEY_RISK
from analysis import TAINTED_PACKAGE_CREATE

DEFAULT_RISKS = {
    INTERNET_RISK : ( "INTERNET_RISK", (195, 255, 0) ),
    PRIVACY_RISK : ( "PRIVACY_RISK", (255, 255, 51) ),
    PHONE_RISK : ( "PHONE_RISK", ( 255, 216, 0 ) ),
    SMS_RISK : ( "SMS_RISK", ( 255, 93, 0 ) ),
    MONEY_RISK : ( "MONEY_RISK", ( 255, 0, 0 ) ),
}

DEXCLASSLOADER_COLOR = (0, 0, 0)
ACTIVITY_COLOR = (51, 255, 51)
SERVICE_COLOR = (0, 204, 204)
RECEIVER_COLOR = (204, 51, 204)

ID_ATTRIBUTES = {
    "type" : 0,
    "class_name" : 1,
    "method_name" : 2,
    "descriptor" : 3,
    "permissions" : 4,
    "permissions_level" : 5,
    "android_api" : 6,
    "java_api" : 7,
    "dynamic_code" : 8,
}

class GVMAnalysis :
    def __init__(self, vmx, apk) :
        self.vmx = vmx
        self.vm = self.vmx.get_vm()

        self.__nodes = {}
        self.__nodes_id = {}
        self.G = DiGraph()

        for j in self.vmx.tainted_packages.get_internal_packages() :
            n1 = self._get_node( j.get_method().get_class_name(), j.get_method().get_name(), j.get_method().get_descriptor() )
            n2 = self._get_node( j.get_class_name(), j.get_name(), j.get_descriptor() )


            m1 = self.vm.get_method_descriptor( j.get_method().get_class_name(), j.get_method().get_name(), j.get_method().get_descriptor()  )
            m2 = j.get_method()

            n1.set_attributes( { "android_api" : libsign.entropy( self.vmx.get_method_signature(m1, "L4", { "L4" : { "arguments" : ["Landroid"] } } ).get_string() ) } )
            n2.set_attributes( { "android_api" : libsign.entropy( self.vmx.get_method_signature(m2, "L4", { "L4" : { "arguments" : ["Landroid"] } } ).get_string() ) } )

            n1.set_attributes( { "java_api" : libsign.entropy( self.vmx.get_method_signature(m1, "L4", { "L4" : { "arguments" : ["Ljava"] } } ).get_string() ) } )
            n2.set_attributes( { "java_api" : libsign.entropy( self.vmx.get_method_signature(m2, "L4", { "L4" : { "arguments" : ["Ljava"] } } ).get_string() ) } )

            self.G.add_edge( n1.id, n2.id )
            
        #    print "\t %s %s %s %x ---> %s %s %s" % (j.get_method().get_class_name(), j.get_method().get_name(), j.get_method().get_descriptor(), \
        #                                            j.get_bb().start + j.get_idx(), \
        #                                            j.get_class_name(), j.get_name(), j.get_descriptor())

        if apk != None :
            for i in apk.get_activities() :
                j = bytecode.FormatClassToJava(i)
                n1 = self._get_exist_node( j, "onCreate", "(Landroid/os/Bundle;)V" )
                if n1 != None : 
                    n1.set_attributes( { "type" : "activity" } )
                    n1.set_attributes( { "color" : ACTIVITY_COLOR } )
                    n2 = self._get_new_node_from( n1, "ACTIVITY" )
                    n2.set_attributes( { "color" : ACTIVITY_COLOR } )
                    self.G.add_edge( n2.id, n1.id )
            for i in apk.get_services() :
                j = bytecode.FormatClassToJava(i)
                n1 = self._get_exist_node( j, "onCreate", "()V" )
                if n1 != None : 
                    n1.set_attributes( { "type" : "service" } )
                    n1.set_attributes( { "color" : SERVICE_COLOR } )
                    n2 = self._get_new_node_from( n1, "SERVICE" )
                    n2.set_attributes( { "color" : SERVICE_COLOR } )
                    self.G.add_edge( n2.id, n1.id )
            for i in apk.get_receivers() :
                j = bytecode.FormatClassToJava(i)
                n1 = self._get_exist_node( j, "onReceive", "(Landroid/content/Context; Landroid/content/Intent;)V" )
                if n1 != None : 
                    n1.set_attributes( { "type" : "receiver" } )
                    n1.set_attributes( { "color" : RECEIVER_COLOR } )
                    n2 = self._get_new_node_from( n1, "RECEIVER" )
                    n2.set_attributes( { "color" : RECEIVER_COLOR } )
                    self.G.add_edge( n2.id, n1.id )

        for c in self.vm.get_classes() :
            #if c.get_superclassname() == "Landroid/app/Service;" :
            #    n1 = self._get_node( c.get_name(), "<init>", "()V" )
            #    n2 = self._get_node( c.get_name(), "onCreate", "()V" )

            #    self.G.add_edge( n1.id, n2.id )
            if c.get_superclassname() == "Ljava/lang/Thread;" :
                for i in self.vm.get_method("run") :
                    if i.get_class_name() == c.get_name() :
                        n1 = self._get_node( i.get_class_name(), i.get_name(), i.get_descriptor() )
                        n2 = self._get_node( i.get_class_name(), "start", i.get_descriptor() ) 
                        
                        self.G.add_edge( n1.id, n2.id )

       
        list_permissions = self.vmx.get_permissions( [] ) 
        for x in list_permissions :
            for j in list_permissions[ x ] :

                #print "\t %s %s %s %x ---> %s %s %s" % (j.get_method().get_class_name(), j.get_method().get_name(), j.get_method().get_descriptor(), \
                #                                    j.get_bb().start + j.get_idx(), \
                #                                    j.get_class_name(), j.get_name(), j.get_descriptor())
                n1 = self._get_exist_node( j.get_method().get_class_name(), j.get_method().get_name(), j.get_method().get_descriptor() )
                
                if n1 == None :
                    continue

                n1.set_attributes( { "permissions" : 1 } )
                n1.set_attributes( { "permissions_level" : DVM_PERMISSIONS[ "MANIFEST_PERMISSION" ][ x ][0] } )
                
                try :
                    for tmp_perm in PERMISSIONS_RISK[ x ] :
                        if tmp_perm in DEFAULT_RISKS :
                            n2 = self._get_new_node( j.get_method().get_class_name(), j.get_method().get_name(), j.get_method().get_descriptor() + " " + DEFAULT_RISKS[ tmp_perm ][0],
                                                     DEFAULT_RISKS[ tmp_perm ][0] )
                            n2.set_attributes( { "color" : DEFAULT_RISKS[ tmp_perm ][1] } )
                            self.G.add_edge( n2.id, n1.id )
                except KeyError :
                    pass

        for m, _ in self.vmx.tainted_packages.get_packages() :
            if m.get_info() == "Ldalvik/system/DexClassLoader;" :
                for path in m.get_paths() :
                    if path.get_access_flag() == TAINTED_PACKAGE_CREATE :
                        n1 = self._get_exist_node( path.get_method().get_class_name(), path.get_method().get_name(), path.get_method().get_descriptor() )    
                        n2 = self._get_new_node( path.get_method().get_class_name(), path.get_method().get_name(), path.get_method().get_descriptor() + " " + "DEXCLASSLOADER",
                                                 "DEXCLASSLOADER" )

                        n1.set_attributes( { "dynamic_code" : "true" } )
                        n2.set_attributes( { "color" : DEXCLASSLOADER_COLOR } )
                        self.G.add_edge( n2.id, n1.id )

    def _get_exist_node(self, class_name, method_name, descriptor) :
        key = "%s %s %s" % (class_name, method_name, descriptor)
        try :
            return self.__nodes[ key ]
        except KeyError :
            return None

    def _get_node(self, class_name, method_name, descriptor) :
        key = "%s %s %s" % (class_name, method_name, descriptor)
        if key not in self.__nodes :
            self.__nodes[ key ] = NodeF( len(self.__nodes), class_name, method_name, descriptor )
            self.__nodes_id[ self.__nodes[ key ].id ] = self.__nodes[ key ]

        return self.__nodes[ key ]

    def _get_new_node_from(self, n, label) :
        return self._get_new_node( n.class_name, n.method_name, n.descriptor + label, label )

    def _get_new_node(self, class_name, method_name, descriptor, label) :
        key = "%s %s %s" % (class_name, method_name, descriptor)
        if key not in self.__nodes :
            self.__nodes[ key ] = NodeF( len(self.__nodes), class_name, method_name, descriptor, label )
            self.__nodes_id[ self.__nodes[ key ].id ] = self.__nodes[ key ]

        return self.__nodes[ key ]

    def export_to_gexf(self, output) :
        fd = open(output, "w")

        fd.write( "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" )
        fd.write( "<gexf xmlns=\"http://www.gephi.org/gexf\" xmlns:viz=\"http://www.gephi.org/gexf/viz\">\n" )
        fd.write( "<graph type=\"static\">\n")

        fd.write( "<attributes class=\"node\" type=\"static\">\n" )
        fd.write( "<attribute default=\"normal\" id=\"%d\" title=\"type\" type=\"string\"/>\n" % ID_ATTRIBUTES[ "type"] )
        fd.write( "<attribute id=\"%d\" title=\"class_name\" type=\"string\"/>\n" % ID_ATTRIBUTES[ "class_name"] )
        fd.write( "<attribute id=\"%d\" title=\"method_name\" type=\"string\"/>\n" % ID_ATTRIBUTES[ "method_name"] )
        fd.write( "<attribute id=\"%d\" title=\"descriptor\" type=\"string\"/>\n" % ID_ATTRIBUTES[ "descriptor"] )


        fd.write( "<attribute default=\"0\" id=\"%d\" title=\"permissions\" type=\"integer\"/>\n" % ID_ATTRIBUTES[ "permissions"] )
        fd.write( "<attribute default=\"normal\" id=\"%d\" title=\"permissions_level\" type=\"string\"/>\n" % ID_ATTRIBUTES[ "permissions_level"] )
        fd.write( "<attribute default=\"0.0\" id=\"%d\" title=\"android_api\" type=\"float\"/>\n" % ID_ATTRIBUTES[ "android_api"] )
        fd.write( "<attribute default=\"0.0\" id=\"%d\" title=\"java_api\" type=\"float\"/>\n" % ID_ATTRIBUTES[ "java_api"] )
        
        fd.write( "<attribute default=\"false\" id=\"%d\" title=\"dynamic_code\" type=\"boolean\"/>\n" % ID_ATTRIBUTES[ "dynamic_code"] )
        fd.write( "</attributes>\n" )   

        fd.write( "<nodes>" )
        for node in self.G.node :
            fd.write( "<node id=\"%d\" label=\"%s\">\n" % (node, escape(self.__nodes_id[ node ].label)) )
            fd.write( self.__nodes_id[ node ].get_attributes() )
            fd.write( "</node>\n" )
        fd.write( "</nodes>\n" )


        fd.write( "<edges>\n" )
        nb = 0
        for edge in self.G.edge :
            for link in self.G.edges( edge ) :
                fd.write( "<edge id=\"%d\" source=\"%d\" target=\"%d\"/>\n" % (nb, link[0], link[1]) )
                nb += 1
        fd.write( "</edges>\n")


        fd.write("</graph>\n")
        fd.write("</gexf>\n")
        fd.close()


DEFAULT_NODE_TYPE = "normal"
DEFAULT_NODE_PERM = 0
DEFAULT_NODE_PERM_LEVEL = -1 

PERMISSIONS_LEVEL = {
    "dangerous" : 3,
    "signatureOrSystem" : 2,
    "signature" : 1,
    "normal" : 0,
}

COLOR_PERMISSIONS_LEVEL = {
    "dangerous"                 : (255, 0, 0),
    "signatureOrSystem"         : (255, 63, 63),
    "signature"                 : (255, 132, 132),
    "normal"                    : (255, 181, 181),
}

class NodeF :
    def __init__(self, id, class_name, method_name, descriptor, label=None) :
        self.class_name = class_name
        self.method_name = method_name 
        self.descriptor = descriptor

        self.id = id

        if label == None : 
            self.label = "%s %s %s" % (class_name, method_name, descriptor)
        else :
            self.label = label

        self.attributes = { "type" : DEFAULT_NODE_TYPE,
                            "color" : None,
                            "permissions" : DEFAULT_NODE_PERM,
                            "permissions_level" : DEFAULT_NODE_PERM_LEVEL,
                            "android_api" : 0.0,
                            "java_api" : 0.0,
                            "dynamic_code" : "false",
                          }

    def get_attributes(self) :
        buff = ""
        
        if self.attributes[ "color" ] != None : 
            buff += "<viz:color r=\"%d\" g=\"%d\" b=\"%d\"/>\n" % (self.attributes[ "color" ][0], self.attributes[ "color" ][1], self.attributes[ "color" ][2])
        
        buff += "<attvalues>\n"
        buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["class_name"], escape(self.class_name))
        buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["method_name"], escape(self.method_name))
        buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["descriptor"], escape(self.descriptor))
        
        
        if self.attributes[ "type" ] != DEFAULT_NODE_TYPE :
            buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["type"], self.attributes[ "type" ])
        if self.attributes[ "permissions" ] != DEFAULT_NODE_PERM :
            buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["permissions"], self.attributes[ "permissions" ])
            buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["permissions_level"], self.attributes[ "permissions_level_name" ])


        buff += "<attvalue id=\"%d\" value=\"%f\"/>\n" % (ID_ATTRIBUTES["android_api"], self.attributes[ "android_api" ])
        buff += "<attvalue id=\"%d\" value=\"%f\"/>\n" % (ID_ATTRIBUTES["java_api"], self.attributes[ "java_api" ])

        buff += "<attvalue id=\"%d\" value=\"%s\"/>\n" % (ID_ATTRIBUTES["dynamic_code"], self.attributes[ "dynamic_code" ])

        buff += "</attvalues>\n"

        return buff

    def set_attributes(self, values) :
        for i in values :
            if i == "permissions" :
                self.attributes[ "permissions" ] += values[i]
            elif i == "permissions_level" :
                if values[i] > self.attributes[ "permissions_level" ] :
                    self.attributes[ "permissions_level" ] = PERMISSIONS_LEVEL[ values[i] ]
                    self.attributes[ "permissions_level_name" ] = values[i]
                    self.attributes[ "color" ] = COLOR_PERMISSIONS_LEVEL[ values[i] ]
            else :
                self.attributes[ i ] = values[i]
