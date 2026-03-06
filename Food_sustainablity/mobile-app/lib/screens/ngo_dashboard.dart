import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../theme.dart';
import 'details_list_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';
import 'emergency_alerts_screen.dart';
import 'food_request_screen.dart';

class NGODashboard extends StatefulWidget {
  const NGODashboard({Key? key}) : super(key: key);

  @override
  State<NGODashboard> createState() => _NGODashboardState();
}

class _NGODashboardState extends State<NGODashboard> {
  bool _isLoading = true;
  List<dynamic> _orders = [];
  String _ngoName = "Loading...";
  int _mealsSecured = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
       _ngoName = prefs.getString('name') ?? 'Hope Shelter';
    });
    await _fetchOrders();
  }

  Future<void> _fetchOrders() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('token') ?? '';
      final userId = prefs.getString('userId') ?? '';

      final response = await http.get(
        Uri.parse('http://localhost:5001/api/orders/list?role=NGO&userId=$userId'),
        headers: {'Authorization': 'Bearer $token'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _orders = data['data'] ?? [];
          _mealsSecured = _orders.where((o) => o['status'] == 'Completed').length * 20; // Mock calculation
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
    } catch (e) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _updateOrderStatus(String orderId, String newStatus) async {
      try {
          final prefs = await SharedPreferences.getInstance();
          final token = prefs.getString('token') ?? '';

          final response = await http.patch(
             Uri.parse('http://localhost:5001/api/orders/$orderId/status'),
             headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
             body: jsonEncode({"status": newStatus})
          );
          
          if (response.statusCode == 200) {
             ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Order $newStatus!'), backgroundColor: Colors.green));
             _fetchOrders();
          }
      } catch (e) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to update status'), backgroundColor: Colors.red));
      }
  }

  String _getAddress(dynamic loc, String fallback) {
      if (loc is Map) return loc['address']?.toString() ?? fallback;
      if (loc is String) return loc;
      return fallback;
  }

  void _promptTransportDecision(String orderId) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Transport Required?'),
        content: const Text('Do you need a delivery partner to transport this food directly to your facility?'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              _processAcceptance(orderId, false);
            },
            child: const Text('No, Will Pickup', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _processAcceptance(orderId, true);
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryGreen),
            child: const Text('Yes, Assign Driver', style: TextStyle(color: Colors.white)),
          )
        ]
      )
    );
  }

  Future<void> _processAcceptance(String orderId, bool needsTransport) async {
      try {
          final prefs = await SharedPreferences.getInstance();
          final token = prefs.getString('token') ?? '';
          final userId = prefs.getString('userId') ?? '';

          final response = await http.patch(
             Uri.parse('http://localhost:5001/api/orders/$orderId/accept'),
             headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer $token'},
             body: jsonEncode({"ngoId": userId, "transportRequested": needsTransport})
          );
          
          if (response.statusCode == 200) {
             ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Order Successfully Claimed!'), backgroundColor: Colors.green));
             _fetchOrders();
          } else {
             final error = jsonDecode(response.body)['error'] ?? 'Failed to accept order';
             ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error), backgroundColor: Colors.red));
          }
      } catch (e) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Connection error'), backgroundColor: Colors.red));
      }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF9FAFC), 
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const EmergencyAlertScreen()));
        },
        backgroundColor: Colors.redAccent,
        icon: const Icon(Icons.warning_amber_rounded, color: Colors.white),
        label: const Text('SOS Alert', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _fetchOrders,
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildTopHeader(),
                const SizedBox(height: 24),
                _buildActionButtons(),
                const SizedBox(height: 24),
                _buildImpactCard(),
                const SizedBox(height: 24),
                _buildGridMenu(),
                const SizedBox(height: 32),
                const Text('Incoming Requests', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1F2937))),
                const SizedBox(height: 16),
                _buildOrdersList(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: _buildActionButton(Icons.check_circle_outline, 'Accept\nDonation', Colors.green, () {
             // Scroll to Incoming Requests or just show message
             ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('See Incoming Requests below to accept.')));
          }),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionButton(Icons.add_shopping_cart, 'Request\nFood', Colors.blue, () {
             Navigator.push(context, MaterialPageRoute(builder: (_) => const FoodRequestScreen()));
          }),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionButton(Icons.vpn_key_outlined, 'Request\nAccess', Colors.orange, () {
             showDialog(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Request Access'),
                  content: const Text('Request administrative access to restricted food bank resources?'),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
                    ElevatedButton(onPressed: () => Navigator.pop(ctx), child: const Text('Request'))
                  ],
                )
             );
          }),
        ),
      ],
    );
  }

  Widget _buildActionButton(IconData icon, String label, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.2)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 8),
            Text(label, textAlign: TextAlign.center, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildTopHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(color: const Color(0xFF0F9D58).withOpacity(0.15), shape: BoxShape.circle),
                  child: const Text('S', style: TextStyle(color: Color(0xFF0F9D58), fontWeight: FontWeight.bold, fontSize: 16)),
                ),
                const SizedBox(width: 12),
                const Text('Smart Food Rescue Network', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1F2937))),
              ],
            ),
            Row(
              children: [
                InkWell(
                   onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NotificationsScreen())),
                   child: Stack(
                     children: [
                       const Icon(Icons.notifications_none, color: Colors.grey),
                       Positioned(
                         right: 2,
                         top: 2,
                         child: Container(width: 8, height: 8, decoration: const BoxDecoration(color: Colors.orange, shape: BoxShape.circle)),
                       )
                     ],
                   ),
                ),
                const SizedBox(width: 16),
                InkWell(
                   onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen())),
                   child: const CircleAvatar(
                     radius: 16,
                     backgroundColor: Colors.blueGrey,
                     child: Icon(Icons.person, color: Colors.white, size: 18),
                   ),
                )
              ]
            )
          ],
        ),
        const SizedBox(height: 32),
        const Text('WELCOME', style: TextStyle(color: Colors.grey, fontSize: 12, letterSpacing: 1.2, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(_ngoName, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: Color(0xFF1F2937))),
      ],
    );
  }

  Widget _buildImpactCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF12B76A), 
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: const Color(0xFF12B76A).withOpacity(0.3), blurRadius: 15, offset: const Offset(0, 5))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Today's Impact", style: TextStyle(color: Colors.white, fontSize: 14)),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(_mealsSecured.toString(), style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
              const SizedBox(width: 8),
              const Text('meals secured', style: TextStyle(color: Colors.white, fontSize: 14)),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildGridMenu() {
    int pendingCount = _orders.where((o) => o['status'] == 'Pending' || o['status'] == 'Driver Assigned').length;
    int trackingCount = _orders.where((o) => o['status'] == 'Accepted' || o['status'] == 'In Transit').length;

    return GridView.count(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 0.9,
      children: [
        _buildGridTile(Icons.inventory_2_outlined, const Color(0xFF12B76A), 'Orders\nReceived', 'Manage incoming requests', () {
           Navigator.push(context, MaterialPageRoute(builder: (_) => const DetailsListScreen(title: 'Orders Received', dataType: 'deliveries')));
        }, badgeCount: pendingCount > 0 ? pendingCount : null),
        _buildGridTile(Icons.location_on_outlined, Colors.orange, 'Nearby Food\nSources', 'Discover available donations', () {
           Navigator.push(context, MaterialPageRoute(builder: (_) => const DetailsListScreen(title: 'Nearby Food', dataType: 'foods')));
        }),
        _buildGridTile(Icons.storage_outlined, Colors.blueAccent, 'Food\nInventory', 'Manage current stock', () {
           Navigator.push(context, MaterialPageRoute(builder: (_) => const DetailsListScreen(title: 'Live Inventory', dataType: 'foods')));
        }),
        _buildGridTile(Icons.history, Colors.purpleAccent, 'Food\nReceived', 'Review past donations', () {
           Navigator.push(context, MaterialPageRoute(builder: (_) => const DetailsListScreen(title: 'Donation History', dataType: 'meals')));
        }),
      ],
    );
  }

  Widget _buildGridTile(IconData icon, Color iconColor, String title, String subtitle, VoidCallback onTap, {int? badgeCount}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 5))],
          border: Border.all(color: Colors.grey.shade100),
        ),
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: iconColor.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
                child: Icon(icon, color: iconColor),
              ),
              const Spacer(),
              Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF1F2937), height: 1.2)),
              const SizedBox(height: 6),
              Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 11, height: 1.2)),
            ],
          ),
          if (badgeCount != null)
            Positioned(
              right: 0,
              top: 0,
              child: Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(color: Colors.redAccent, shape: BoxShape.circle, border: Border.all(color: Colors.white, width: 2)),
                child: Text('$badgeCount', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
              ),
            ),
        ],
      ),
    ),
  );
}

  Widget _buildOrdersList() {
      if (_isLoading) return const Center(child: CircularProgressIndicator());
      if (_orders.isEmpty) return const Center(child: Text('No active orders found.', style: TextStyle(color: Colors.grey)));

      return ListView.builder(
         physics: const NeverScrollableScrollPhysics(),
         shrinkWrap: true,
         itemCount: _orders.length,
         itemBuilder: (context, index) {
            final order = _orders[index];
            bool isPending = order['status'] == 'Pending';

            return Container(
               margin: const EdgeInsets.only(bottom: 16),
               padding: const EdgeInsets.all(16),
               decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 5))],
                  border: Border.all(color: Colors.grey.shade100),
               ),
               child: Column(
                 crossAxisAlignment: CrossAxisAlignment.start,
                 children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                         Text(order['orderIdString'] ?? '#UNKNOWN', style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF12B76A))),
                         Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                               color: (order['status'] == 'Accepted' && order['transportRequested'] == true && order['driverId'] == null)
                               ? Colors.orange.withOpacity(0.1)
                               : Colors.blue.withOpacity(0.1),
                               borderRadius: BorderRadius.circular(8)
                            ),
                            child: Text(
                               (order['status'] == 'Accepted' && order['transportRequested'] == true && order['driverId'] == null)
                               ? 'Awaiting Driver'
                               : order['status'],
                               style: TextStyle(
                                  color: (order['status'] == 'Accepted' && order['transportRequested'] == true && order['driverId'] == null)
                                  ? Colors.orange
                                  : Colors.blue,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold
                               )
                            ),
                         )
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.business, size: 16, color: Colors.grey),
                        const SizedBox(width: 8),
                        Expanded(child: Text("From: ${order['donorId']?['profileName'] ?? 'Unknown Donor'}", style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1F2937)))),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.location_on, size: 16, color: Colors.grey),
                        const SizedBox(width: 8),
                        Expanded(child: Text(_getAddress(order['donorId']?['location'], 'Location not provided'), style: const TextStyle(color: Colors.grey, fontSize: 13))),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (isPending)
                      Row(
                         children: [
                            Expanded(
                               child: ElevatedButton(
                                  onPressed: () => _updateOrderStatus(order['_id'], 'Rejected'),
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                                  child: const Text('Reject', style: TextStyle(color: Colors.white)),
                               ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                               child: ElevatedButton(
                                  onPressed: () => _promptTransportDecision(order['_id']),
                                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF12B76A), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
                                  child: const Text('Accept', style: TextStyle(color: Colors.white)),
                               ),
                            ),
                         ],
                      )
                 ],
               ),
            );
         },
      );
  }
}
