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
                              onTap: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (context) =>
                                            MarkovRecommendationPage(
                                              page: pages[index],
                                              clCode: selectedClCode,
                                            )));
                              },
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
        'https://nivres.com/api/getpages?term=$searchString&cCode=$cCode&lCode=$lCode');
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
    var url = Uri.parse('https://nivres.com/api/getclcodes');
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

class MarkovRecommendationPage extends StatefulWidget {
  const MarkovRecommendationPage(
      {super.key, required this.page, required this.clCode});
  final MathCenterPage page;
  final String clCode;

  @override
  State<MarkovRecommendationPage> createState() =>
      _MarkovRecommendationPageState();
}

class _MarkovRecommendationPageState extends State<MarkovRecommendationPage> {
  var isLoading = true;
  var recommendations = List<RecMathCenterPage>.empty(growable: true);
  final gradesMap = {
    'pre-k': 'prek',
    'kindergarten': 'kindergarten',
    '1st': 'first',
    '2nd': 'second',
    '3rd': 'third',
    '4th': 'fourth',
    '5th': 'fifth',
    '6th': 'sixth',
    '7th': 'seventh',
    '8th': 'eighth'
  };
  @override
  void initState() {
    super.initState();
    fetchRecommendations();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Markov Recommendations'),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SelectableText(
                widget.page.name,
                style: const TextStyle(
                    fontSize: 20.0,
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.bold),
              ),
              IconButton(
                  onPressed: () {
                    showModalBottomSheet(
                        context: context,
                        builder: (context) => PageSheetInfo(page: widget.page));
                  },
                  icon: const Icon(Icons.info_outline))
            ],
          ),
          const SizedBox(height: 20),
          const Text(
            'Recommendations',
            style: TextStyle(
                fontSize: 18.0,
                fontStyle: FontStyle.italic,
                fontWeight: FontWeight.bold),
          ),
          isLoading
              ? const Center(
                  child: CircularProgressIndicator(),
                )
              : Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      children: List.generate(
                          recommendations.length,
                          (index) => Padding(
                                padding: const EdgeInsets.all(8.0),
                                child: ListTile(
                                  title: Text(recommendations[index].name),
                                  subtitle: Text(recommendations[index].uid),
                                  trailing: Text(recommendations[index].model),
                                  onTap: () {
                                    showModalBottomSheet(
                                        context: context,
                                        builder: (context) => PageSheetInfo(
                                            page: MathCenterPage
                                                .fromRecMathCenterPage(
                                                    recommendations[index])));
                                  },
                                ),
                              )),
                    ),
                  ),
                )
        ],
      ),
    );
  }

  void fetchRecommendations() async {
    setState(() {
      isLoading = true;
    });

    var splitCl = widget.clCode.split("-");
    var cCode = splitCl[0], lCode = splitCl[1];

    var url = Uri.parse('https://nivres.com/api/markov');
    var body = jsonEncode({
      "uid": [widget.page.uid],
      "cCode": cCode,
      "lCode": lCode,
      "grade": [
        gradesMap[widget.page.minGrade],
        gradesMap[widget.page.maxGrade]
      ],
      // "n": 10,
    });
    var headers = {"Content-Type": "application/json"};
    var response = await http.post(url, body: body, headers: headers);
    var data = List<dynamic>.empty(growable: true);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      data = json.decode(response.body);

      setState(() {
        isLoading = false;
        recommendations =
            data.map((e) => RecMathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}
