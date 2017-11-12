#include <iostream>
#include <net/inet4>
#include <net/ip4/cidr.hpp>
#include <plugins/nacl.hpp>
#include <net/nat/napt.hpp>
#include <net/router.hpp>

using namespace net;

std::unique_ptr<Router<IP4>> nacl_router_obj;
std::shared_ptr<Conntrack> nacl_ct_obj;
std::unique_ptr<nat::NAPT> nacl_natty_obj;

namespace custom_made_classes_from_nacl {

class Eth_Test_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_src() == IP4::addr{10,0,0,99} or pckt.ip_src() == IP4::addr{10,10,10,10} or pckt.ip_src() == IP4::addr{255,255,255,0} or pckt.ip_src() == IP4::addr{10,0,0,1}) {
return Filter_verdict::ACCEPT;
}
return Filter_verdict::DROP;

	}
};

class An_Udp_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::UDP) {
auto& udp_pckt = static_cast<PacketUDP&>(pckt);

if (udp_pckt.src_port() == 80) {
return Filter_verdict::ACCEPT;
}
}

	}
};

class Main_Ip_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if ((!((pckt.ip_src() == IP4::addr{140,50,200,55} or pckt.ip_src() == IP4::addr{255,255,255,0}) and pckt.ip_dst() < IP4::addr{10,0,0,45} and pckt.ip_src() < IP4::addr{10,0,0,45}) and (pckt.ip_checksum() < 400 or (true and pckt.ip_ttl() > 50)))) {
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if (tcp_pckt.src_port() == 53) {
return Filter_verdict::DROP;
}
if (tcp_pckt.ip_dst() == IP4::addr{132,23,30,5}) {
return Filter_verdict::DROP;
}
if (tcp_pckt.ip_dst() == IP4::addr{132,23,30,5}) {
return Filter_verdict::DROP;
}
if (tcp_pckt.dst_port() == 80) {
if (tcp_pckt.ip_version() == 6) {
return Filter_verdict::DROP;
}
else {
return Filter_verdict::ACCEPT;
}
}
else {
return Filter_verdict::ACCEPT;
}
if (tcp_pckt.ip_dst() == IP4::addr{10,0,0,55}) {
return Filter_verdict::DROP;
}
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (icmp_pckt.ip().ip_dst() == IP4::addr{120,30,20,10}) {
return Filter_verdict::ACCEPT;
}
if (icmp_pckt.ip().ip_dst() == IP4::addr{10,0,0,55}) {
return Filter_verdict::DROP;
}
}
if (pckt.ip_protocol() == Protocol::UDP) {
auto& udp_pckt = static_cast<PacketUDP&>(pckt);

if (udp_pckt.dst_port() == 443) {
return Filter_verdict::ACCEPT;
}
else {
if ((udp_pckt.dst_port() == 50 or udp_pckt.dst_port() == 53 or udp_pckt.dst_port() == 77 or (udp_pckt.dst_port() >= 8080 and udp_pckt.dst_port() <= 8090) or udp_pckt.dst_port() == 46 or udp_pckt.dst_port() == 99 or (udp_pckt.dst_port() >= 65 and udp_pckt.dst_port() <= 68) or udp_pckt.dst_port() == 102) and udp_pckt.ip_checksum() > 4040) {
return Filter_verdict::ACCEPT;
}
}
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (icmp_pckt.ip().ip_ttl() > 33 and icmp_pckt.type() != icmp4::Type::DEST_UNREACHABLE) {
return Filter_verdict::DROP;
}
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if (tcp_pckt.ip_dst() == IP4::addr{10,0,0,40} and tcp_pckt.dst_port() == 80) {
return Filter_verdict::ACCEPT;
}
}
if ((pckt.ip_dst() == IP4::addr{10,0,0,40} or ip4::Cidr{120,30,20,0,24}.contains(pckt.ip_dst()) or pckt.ip_dst() == IP4::addr{140,20,10,13} or (pckt.ip_dst() >= IP4::addr{140,20,10,20} and pckt.ip_dst() <= IP4::addr{140,20,10,100}))) {
if ((pckt.ip_src() >= IP4::addr{126,21,28,44} and pckt.ip_src() <= IP4::addr{126,21,29,10})) {
return Filter_verdict::DROP;
}
else {
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if (tcp_pckt.dst_port() == 8080) {
return Filter_verdict::ACCEPT;
}
if (tcp_pckt.ip_dst() == IP4::addr{10,0,0,40} and tcp_pckt.dst_port() == 80) {
return Filter_verdict::ACCEPT;
}
}
return Filter_verdict::ACCEPT;
return Filter_verdict::DROP;

	}
};

class Hierarchy_Test_2 : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::UDP) {
auto& udp_pckt = static_cast<PacketUDP&>(pckt);

if (udp_pckt.ip_dst() == IP4::addr{10,0,0,55}) {
return Filter_verdict::DROP;
}
if ((udp_pckt.dst_port() == 50 or udp_pckt.dst_port() == 53 or udp_pckt.dst_port() == 77 or (udp_pckt.dst_port() >= 8080 and udp_pckt.dst_port() <= 8090) or udp_pckt.dst_port() == 46 or udp_pckt.dst_port() == 99 or (udp_pckt.dst_port() >= 65 and udp_pckt.dst_port() <= 68) or udp_pckt.dst_port() == 102) and udp_pckt.ip_checksum() > 4040) {
return Filter_verdict::ACCEPT;
}
}

	}
};

class Main_Icmp_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (!(icmp_pckt.type() == icmp4::Type::TIMESTAMP and !((icmp_pckt.ip().ip_src() >= IP4::addr{126,21,28,44} and icmp_pckt.ip().ip_src() <= IP4::addr{126,21,29,10}))) and !(icmp_pckt.ip().ip_ttl() > 30)) {
return Filter_verdict::DROP;
}
if (ct_entry->state != Conntrack::State::ESTABLISHED) {
return Filter_verdict::DROP;
}
return Filter_verdict::ACCEPT;
}

	}
};

class Ip_Filter_Equals : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if ((pckt.ip_dst() == IP4::addr{10,0,0,40} or ip4::Cidr{120,30,20,0,24}.contains(pckt.ip_dst()) or pckt.ip_dst() == IP4::addr{140,20,10,13} or (pckt.ip_dst() >= IP4::addr{140,20,10,20} and pckt.ip_dst() <= IP4::addr{140,20,10,100}))) {
if ((pckt.ip_src() >= IP4::addr{126,21,28,44} and pckt.ip_src() <= IP4::addr{126,21,29,10})) {
return Filter_verdict::DROP;
}
else {
return Filter_verdict::ACCEPT;
}
}

	}
};

class Hierarchy_Test : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (icmp_pckt.ip().ip_ttl() > 33 and icmp_pckt.type() != icmp4::Type::DEST_UNREACHABLE) {
return Filter_verdict::DROP;
}
return Filter_verdict::ACCEPT;
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (icmp_pckt.ip().ip_version() < 6 and icmp_pckt.type() == icmp4::Type::ECHO) {
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_protocol() == Protocol::UDP) {
auto& udp_pckt = static_cast<PacketUDP&>(pckt);

if ((udp_pckt.dst_port() == 50 or udp_pckt.dst_port() == 53 or udp_pckt.dst_port() == 77 or (udp_pckt.dst_port() >= 8080 and udp_pckt.dst_port() <= 8090) or udp_pckt.dst_port() == 46 or udp_pckt.dst_port() == 99 or (udp_pckt.dst_port() >= 65 and udp_pckt.dst_port() <= 68) or udp_pckt.dst_port() == 102) and udp_pckt.ip_checksum() > 4040) {
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_protocol() == Protocol::UDP) {
auto& udp_pckt = static_cast<PacketUDP&>(pckt);

if (udp_pckt.ip_version() < 6 and udp_pckt.src_port() == 80) {
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if ((tcp_pckt.ip_src() >= IP4::addr{10,10,20,3} and tcp_pckt.ip_src() <= IP4::addr{10,10,20,55}) and tcp_pckt.ack() > 30) {
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if ((tcp_pckt.ip_src() >= IP4::addr{10,10,20,14} and tcp_pckt.ip_src() <= IP4::addr{10,10,20,60}) and tcp_pckt.ack() > 33) {
return Filter_verdict::ACCEPT;
}
}
if (pckt.ip_dst() == IP4::addr{10,0,0,55}) {
return Filter_verdict::DROP;
}
if (pckt.ip_checksum() > 400) {
return Filter_verdict::DROP;
}

	}
};

class An_Ip_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_dst() == IP4::addr{10,0,0,55}) {
return Filter_verdict::DROP;
}

	}
};

class Tcp_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if ((tcp_pckt.ip_src() >= IP4::addr{10,10,20,3} and tcp_pckt.ip_src() <= IP4::addr{10,10,20,55}) and tcp_pckt.ack() > 30) {
return Filter_verdict::ACCEPT;
}
}

	}
};

class Ip_Filter_Not_Equals : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (!((pckt.ip_dst() == IP4::addr{10,0,0,40} or ip4::Cidr{120,30,20,0,24}.contains(pckt.ip_dst()) or pckt.ip_dst() == IP4::addr{140,20,10,13} or (pckt.ip_dst() >= IP4::addr{140,20,10,20} and pckt.ip_dst() <= IP4::addr{140,20,10,100})))) {
return Filter_verdict::DROP;
}
if (!(ip4::Cidr{120,20,30,0,24}.contains(pckt.ip_dst()))) {
return Filter_verdict::DROP;
}
if (!((pckt.ip_dst() >= IP4::addr{10,20,30,1} and pckt.ip_dst() <= IP4::addr{10,20,30,40}))) {
return Filter_verdict::DROP;
}
if (!((pckt.ip_src() == IP4::addr{10,0,0,1} or ip4::Cidr{190,50,20,0,24}.contains(pckt.ip_src()) or (pckt.ip_src() >= IP4::addr{180,20,30,0} and pckt.ip_src() <= IP4::addr{180,20,30,50}) or (pckt.ip_src() >= IP4::addr{180,20,30,100} and pckt.ip_src() <= IP4::addr{180,20,30,150}) or pckt.ip_src() == IP4::addr{180,20,30,155}))) {
return Filter_verdict::ACCEPT;
}

	}
};

class Main_Tcp_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::TCP) {
auto& tcp_pckt = static_cast<tcp::Packet&>(pckt);

if (tcp_pckt.ip_dst() == IP4::addr{10,0,0,102} or tcp_pckt.ip_dst() == IP4::addr{10,0,0,80} or tcp_pckt.ip_dst() == IP4::addr{10,0,0,203} or tcp_pckt.src_port() == 2800) {
return Filter_verdict::ACCEPT;
}
if (tcp_pckt.dst_port() == 55) {
return Filter_verdict::ACCEPT;
}
if ((tcp_pckt.ip_dst() == IP4::addr{10,0,0,40} or ip4::Cidr{120,30,20,0,24}.contains(tcp_pckt.ip_dst()) or tcp_pckt.ip_dst() == IP4::addr{140,20,10,13} or (tcp_pckt.ip_dst() >= IP4::addr{140,20,10,20} and tcp_pckt.ip_dst() <= IP4::addr{140,20,10,100}))) {
if ((tcp_pckt.ip_src() >= IP4::addr{126,21,28,44} and tcp_pckt.ip_src() <= IP4::addr{126,21,29,10})) {
return Filter_verdict::DROP;
}
else {
return Filter_verdict::ACCEPT;
}
}
if ((tcp_pckt.ip_src() >= IP4::addr{10,10,20,3} and tcp_pckt.ip_src() <= IP4::addr{10,10,20,55}) and tcp_pckt.ack() > 30) {
return Filter_verdict::ACCEPT;
}
if (tcp_pckt.ip_version() == 4) {
return Filter_verdict::ACCEPT;
}
if (tcp_pckt.ack() <= 88) {
if ((tcp_pckt.src_port() == 40 or tcp_pckt.src_port() == 443 or (tcp_pckt.src_port() >= 77 and tcp_pckt.src_port() <= 90) or tcp_pckt.src_port() == 44 or (tcp_pckt.src_port() >= 99 and tcp_pckt.src_port() <= 101) or tcp_pckt.src_port() == 100 or tcp_pckt.src_port() == 2800) or tcp_pckt.dst_port() == 80) {
return Filter_verdict::ACCEPT;
}
else {
if ((tcp_pckt.ip_ttl() >= 10 and tcp_pckt.ip_ttl() <= 201) or ((tcp_pckt.ip_ttl() > 30 and tcp_pckt.ip_checksum() > 33) or ((tcp_pckt.dst_port() >= 20 and tcp_pckt.dst_port() <= 30) or tcp_pckt.ip_src() == IP4::addr{10,0,0,40}))) {
return Filter_verdict::DROP;
}
else {
if (!((tcp_pckt.ip_dst() == IP4::addr{10,0,0,40} or ip4::Cidr{120,30,20,0,24}.contains(tcp_pckt.ip_dst()) or tcp_pckt.ip_dst() == IP4::addr{140,20,10,13} or (tcp_pckt.ip_dst() >= IP4::addr{140,20,10,20} and tcp_pckt.ip_dst() <= IP4::addr{140,20,10,100})))) {
return Filter_verdict::DROP;
}
if (!(ip4::Cidr{120,20,30,0,24}.contains(tcp_pckt.ip_dst()))) {
return Filter_verdict::DROP;
}
if (!((tcp_pckt.ip_dst() >= IP4::addr{10,20,30,1} and tcp_pckt.ip_dst() <= IP4::addr{10,20,30,40}))) {
return Filter_verdict::DROP;
}
if (!((tcp_pckt.ip_src() == IP4::addr{10,0,0,1} or ip4::Cidr{190,50,20,0,24}.contains(tcp_pckt.ip_src()) or (tcp_pckt.ip_src() >= IP4::addr{180,20,30,0} and tcp_pckt.ip_src() <= IP4::addr{180,20,30,50}) or (tcp_pckt.ip_src() >= IP4::addr{180,20,30,100} and tcp_pckt.ip_src() <= IP4::addr{180,20,30,150}) or tcp_pckt.ip_src() == IP4::addr{180,20,30,155}))) {
return Filter_verdict::ACCEPT;
}
return Filter_verdict::ACCEPT;
}
}
}
return Filter_verdict::DROP;
}

	}
};

class Hierarchy_Test_3 : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (icmp_pckt.ip().ip_dst() == IP4::addr{10,0,0,55}) {
return Filter_verdict::DROP;
}
if (icmp_pckt.ip().ip_ttl() > 33 and icmp_pckt.type() != icmp4::Type::DEST_UNREACHABLE) {
return Filter_verdict::DROP;
}
return Filter_verdict::ACCEPT;
return Filter_verdict::ACCEPT;
if (icmp_pckt.ip().ip_ttl() > 33 and icmp_pckt.type() != icmp4::Type::DEST_UNREACHABLE) {
return Filter_verdict::DROP;
}
return Filter_verdict::ACCEPT;
if (icmp_pckt.type() == icmp4::Type::TIMESTAMP) {
return Filter_verdict::ACCEPT;
}
return Filter_verdict::ACCEPT;
return Filter_verdict::ACCEPT;
}

	}
};

class Icmp_Filter : public nacl::Filter {
public:
	Filter_verdict operator()(IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr ct_entry) {
		if (not ct_entry) {
return Filter_verdict::DROP;
}
if (pckt.ip_protocol() == Protocol::ICMPv4) {
auto& icmp_pckt = *(icmp4::Packet*) &pckt;

if (icmp_pckt.ip().ip_ttl() > 33 and icmp_pckt.type() != icmp4::Type::DEST_UNREACHABLE) {
return Filter_verdict::DROP;
}
return Filter_verdict::ACCEPT;
}

	}
};

} //< namespace custom_made_classes_from_nacl

void register_plugin_nacl() {
	INFO("NaCl", "Registering NaCl plugin");

	auto& eth4 = Inet4::stack<3>();
	eth4.network_config(IP4::addr{10,0,0,203}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
	auto& eth3 = Inet4::stack<2>();
	eth3.network_config(IP4::addr{10,0,0,102}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
	auto& eth1 = Inet4::stack<5>();
	eth1.network_config(IP4::addr{10,0,0,80}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1});
	auto& eth0 = Inet4::stack<4>();
	eth0.network_config(IP4::addr{10,0,0,40}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1}, IP4::addr{8,8,8,8});
	auto& eth_test_2 = Inet4::stack<1>();
	eth_test_2.network_config(IP4::addr{10,0,0,99}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1}, IP4::addr{10,10,10,10});
	auto& eth2 = Inet4::stack<6>();
	Inet4::ifconfig<6>(10.0, [&eth2] (bool timedout) {
		if (timedout) {
			INFO("NaCl plugin interface eth2", "DHCP request timed out. Nothing to do.");
			return;
		}
		INFO("NaCl plugin interface eth2", "IP address updated: %s", eth2.ip_addr().str().c_str());
	});
	auto& eth_test_1 = Inet4::stack<0>();
	eth_test_1.network_config(IP4::addr{10,0,0,130}, IP4::addr{255,255,255,0}, IP4::addr{10,0,0,1}, IP4::addr{9,9,9,9});

	custom_made_classes_from_nacl::Eth_Test_Filter eth_test_filter;
	custom_made_classes_from_nacl::An_Udp_Filter an_udp_filter;
	custom_made_classes_from_nacl::Main_Ip_Filter main_ip_filter;
	custom_made_classes_from_nacl::Hierarchy_Test_2 hierarchy_test_2;
	custom_made_classes_from_nacl::Main_Icmp_Filter main_icmp_filter;
	custom_made_classes_from_nacl::Ip_Filter_Equals ip_filter_equals;
	custom_made_classes_from_nacl::Hierarchy_Test hierarchy_test;
	custom_made_classes_from_nacl::An_Ip_Filter an_ip_filter;
	custom_made_classes_from_nacl::Tcp_Filter tcp_filter;
	custom_made_classes_from_nacl::Ip_Filter_Not_Equals ip_filter_not_equals;
	custom_made_classes_from_nacl::Main_Tcp_Filter main_tcp_filter;
	custom_made_classes_from_nacl::Hierarchy_Test_3 hierarchy_test_3;
	custom_made_classes_from_nacl::Icmp_Filter icmp_filter;

	eth0.ip_obj().postrouting_chain().chain.push_back(main_icmp_filter);

	eth0.ip_obj().input_chain().chain.push_back(main_ip_filter);
	eth0.ip_obj().input_chain().chain.push_back(main_tcp_filter);

	eth_test_1.ip_obj().input_chain().chain.push_back(eth_test_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(tcp_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(main_icmp_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(main_ip_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(icmp_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(ip_filter_equals);
	eth_test_1.ip_obj().input_chain().chain.push_back(ip_filter_not_equals);
	eth_test_1.ip_obj().input_chain().chain.push_back(hierarchy_test_3);
	eth_test_1.ip_obj().input_chain().chain.push_back(hierarchy_test_2);
	eth_test_1.ip_obj().input_chain().chain.push_back(hierarchy_test);
	eth_test_1.ip_obj().input_chain().chain.push_back(an_udp_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(an_ip_filter);
	eth_test_1.ip_obj().input_chain().chain.push_back(main_tcp_filter);

	eth_test_1.ip_obj().prerouting_chain().chain.push_back(eth_test_filter);
	eth_test_1.ip_obj().prerouting_chain().chain.push_back(tcp_filter);
	eth_test_1.ip_obj().prerouting_chain().chain.push_back(main_icmp_filter);

	// Router

	INFO("NaCl", "Setup routing");
	Router<IP4>::Routing_table routing_table {
		{ IP4::addr{140,50,240,0}, IP4::addr{255,255,255,0}, 0, eth3, 1 },
		{ IP4::addr{140,50,200,0}, IP4::addr{255,255,255,0}, IP4::addr{140,50,200,55}, eth1, 1 },
		{ IP4::addr{140,50,100,0}, IP4::addr{255,255,255,0}, IP4::addr{140,50,100,1}, eth0, 100 },
		{ IP4::addr{150,20,23,3}, IP4::addr{255,255,255,0}, 0, eth0, 1 },
		{ IP4::addr{140,50,210,0}, IP4::addr{255,255,255,0}, IP4::addr{140,50,210,1}, eth2, 100 }
	};
	nacl_router_obj = std::make_unique<Router<IP4>>(routing_table);
	// Set ip forwarding on every iface mentioned in routing_table
	eth3.set_forward_delg(nacl_router_obj->forward_delg());
	eth1.set_forward_delg(nacl_router_obj->forward_delg());
	eth0.set_forward_delg(nacl_router_obj->forward_delg());
	eth2.set_forward_delg(nacl_router_obj->forward_delg());

	// Ct

	nacl_ct_obj = std::make_shared<Conntrack>();

	INFO("NaCl", "Enabling Conntrack on eth3");
	eth3.enable_conntrack(nacl_ct_obj);

	INFO("NaCl", "Enabling Conntrack on eth1");
	eth1.enable_conntrack(nacl_ct_obj);

	INFO("NaCl", "Enabling Conntrack on eth0");
	eth0.enable_conntrack(nacl_ct_obj);

	INFO("NaCl", "Enabling Conntrack on eth2");
	eth2.enable_conntrack(nacl_ct_obj);

	INFO("NaCl", "Enabling Conntrack on eth_test_1");
	eth_test_1.enable_conntrack(nacl_ct_obj);

	// NAT

	nacl_natty_obj = std::make_unique<nat::NAPT>(nacl_ct_obj);

	auto masq = [](IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr entry)->auto {
		nacl_natty_obj->masquerade(pckt, stack, entry);
		return Filter_verdict::ACCEPT;
	};
	auto demasq = [](IP4::IP_packet& pckt, Inet<IP4>& stack, Conntrack::Entry_ptr entry)->auto {
		nacl_natty_obj->demasquerade(pckt, stack, entry);
		return Filter_verdict::ACCEPT;
	};

	INFO("NaCl", "Enable MASQUERADE on eth3");
	eth3.ip_obj().prerouting_chain().chain.push_back(demasq);
	eth3.ip_obj().postrouting_chain().chain.push_back(masq);
}