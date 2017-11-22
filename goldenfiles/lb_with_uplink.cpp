#include <iostream>
#include <net/inet4>
#include <net/ip4/cidr.hpp>
#include <plugins/nacl.hpp>
#include <microLB>

using namespace net;

static microLB::Balancer* nacl_lb_obj = nullptr;
void register_plugin_nacl() {
	INFO("NaCl", "Registering NaCl plugin");

	auto& outside = Inet4::stack<1>();
	outside.network_config(IP4::addr{10,0,0,43}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
	auto& inside = Inet4::stack<2>();
	inside.network_config(IP4::addr{10,0,0,44}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
	auto& uplink = Inet4::stack<0>();
	uplink.network_config(IP4::addr{10,0,0,42}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});


	// Load balancers

	inside.tcp().set_MSL(15s);
	nacl_lb_obj = new microLB::Balancer(outside, 80, inside);

	Socket socket_0{ IP4::addr{10,0,0,1}, 6001 };
	nacl_lb_obj->nodes.add_node(inside, socket_0, nacl_lb_obj->get_pool_signal());

	Socket socket_1{ IP4::addr{10,0,0,1}, 6002 };
	nacl_lb_obj->nodes.add_node(inside, socket_1, nacl_lb_obj->get_pool_signal());

	Socket socket_2{ IP4::addr{10,0,0,1}, 6003 };
	nacl_lb_obj->nodes.add_node(inside, socket_2, nacl_lb_obj->get_pool_signal());

	Socket socket_3{ IP4::addr{10,0,0,1}, 6004 };
	nacl_lb_obj->nodes.add_node(inside, socket_3, nacl_lb_obj->get_pool_signal());

	/*
	Name: lb
	Layer: tcp

	Clients iface: outside
	Clients port: 80
	Clients wait queue limit: 1000
	Clients session limit: 1000

	Servers iface: inside
	Servers algorithm: round_robin
	Servers pool:

	Node address: IP4::addr{10,0,0,1}
	Node port: 6001

	Node address: IP4::addr{10,0,0,1}
	Node port: 6002

	Node address: IP4::addr{10,0,0,1}
	Node port: 6003

	Node address: IP4::addr{10,0,0,1}
	Node port: 6004
	*/
}