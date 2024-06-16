import 'dart:convert';
import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:recui/json_classess.dart';
import 'package:recui/user_similarity_page.dart';

class MarkovPage extends StatefulWidget {
  const MarkovPage({super.key});

  @override
  State<MarkovPage> createState() => _MarkovPageState();
}

class _MarkovPageState extends State<MarkovPage> {
  var isLoading = false;

  var clCodes = List<String>.empty(growable: true);

  var pages = List<MathCenterPage>.empty(growable: true);

  var selectedClCode = '';

  @override
  void initState() {
    super.initState();
    getClCodes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Markov Model'),
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text(
                    'Choose cl-code',
                    style: TextStyle(
                      fontStyle: FontStyle.italic,
                      fontWeight: FontWeight.bold,
                      fontSize: 14.0,
                    ),
                  ),
                ),
                ...List.generate(
                  clCodes.length,
                  (index) => Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: ChoiceChip.elevated(
                      label: Text(
                        clCodes[index],
                        style: const TextStyle(fontSize: 12.0),
                      ),
                      selected: clCodes[index] == selectedClCode,
                      onSelected: (value) {
                        setState(() {
                          selectedClCode = clCodes[index];
                        });
                      },
                    ),
                  ),
                ),
              ],
            ),
          ),
          SearchBar(
            hintText: 'Search for page in Math-Center',
            onSubmitted: (value) {
              var splitCl = selectedClCode.split("-");
              var cCode = splitCl[0], lCode = splitCl[1];
              searchPage(value, cCode, lCode);
            },
          ),
          const SizedBox(
            height: 10,
          ),
          isLoading
              ? const CircularProgressIndicator()
              : Expanded(
                  child: ListView(
                    cacheExtent: 10,
                    addAutomaticKeepAlives: false,
                    children: List.generate(
                        pages.length,
                        (index) => ListTile(
                              title: Text(pages[index].name),
                              subtitle: Text(pages[index].uid),
                              onTap: () {},
                              onLongPress: () {
                                showModalBottomSheet(
                                    context: context,
                                    builder: (context) {
                                      return PageSheetInfo(page: pages[index]);
                                    });
                              },
                            )),
                  ),
                ),
        ],
      ),
    );
  }

  Future<void> searchPage(
      String searchString, String cCode, String lCode) async {
    setState(() {
      isLoading = true;
    });
    var url = Uri.parse(
        'http://127.0.0.1:5000/api/getpages?term=$searchString&cCode=$cCode&lCode=$lCode');
    var response = await http.get(url);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      List<dynamic> data = json.decode(response.body);
      // print(data);
      setState(() {
        isLoading = false;
        pages = data.map((e) => MathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }

  void getClCodes() async {
    var url = Uri.parse('http://127.0.0.1:5000/api/getclcodes');
    var response = await http.get(url);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      List<dynamic> data = json.decode(response.body);
      setState(() {
        clCodes = data.map<String>((e) => e).toList();
        clCodes.sort();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}
