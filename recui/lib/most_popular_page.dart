import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:recui/UserSimilarityPage.dart';

import 'dart:developer';

import 'package:recui/json_classess.dart';

class MostPopularPage extends StatefulWidget {
  const MostPopularPage({super.key});

  @override
  State<MostPopularPage> createState() => _MostPopularPageState();
}

class _MostPopularPageState extends State<MostPopularPage> {
  var isSelected = false;
  var clCodes = List<String>.empty(growable: true);

  @override
  void initState() {
    super.initState();
    getClCodes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Most Popular"),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CustomPopularSearch(clCodes: clCodes),
          // MostPopularByCL(clCodes: clCodes),
        ],
      ),
    );
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

class MostPopularByCL extends StatefulWidget {
  const MostPopularByCL({super.key, required this.clCodes});
  final List<String> clCodes;

  @override
  State<MostPopularByCL> createState() => _MostPopularByCLState();
}

class _MostPopularByCLState extends State<MostPopularByCL> {
  var isShowingPopularForCL = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextButton.icon(
          onPressed: () {
            setState(() {
              isShowingPopularForCL = !isShowingPopularForCL;
            });
          },
          icon: Icon(isShowingPopularForCL
              ? Icons.arrow_drop_up
              : Icons.arrow_drop_down),
          label: const Text(
            "Most Popular By Country-Language",
            style: TextStyle(
                fontStyle: FontStyle.italic,
                fontSize: 20.0,
                fontWeight: FontWeight.bold),
          ),
        ),
        ...(!isShowingPopularForCL
            ? [const SizedBox()]
            : [
                const Text(
                  "Custom Popular Search",
                  style: TextStyle(
                      fontStyle: FontStyle.italic,
                      fontSize: 20.0,
                      fontWeight: FontWeight.bold),
                )
              ]),
      ],
    );
  }
}

class CustomPopularSearch extends StatefulWidget {
  const CustomPopularSearch({super.key, required this.clCodes});

  final List<String> clCodes;

  @override
  State<CustomPopularSearch> createState() => _CustomPopularSearchState();
}

class _CustomPopularSearchState extends State<CustomPopularSearch> {
  var isMakingCustom = false;
  var customHasResults = false;

  var selectedClCode = "";

  var selectedGrades = List<String>.empty(growable: true);
  var selectedMonths = List<int>.empty(growable: true);

  var mostPopulars = List<MathCenterPage>.empty(growable: true);

  // final months = [1];
  final months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  final grades = [
    'pre-Kindergarten',
    'Kindergarten',
    'First',
    'Second',
    'Third',
    'Fourth',
    'Fifth',
    'Sixth',
    'Seventh',
    'Eighth'
  ];
  final gradesMap = {
    'pre-Kindergarten': 'prek',
    'Kindergarten': 'kindergarten',
    'First': 'first',
    'Second': 'second',
    'Third': 'third',
    'Fourth': 'fourth',
    'Fifth': 'fifth',
    'Sixth': 'sixth',
    'Seventh': 'seventh',
    'Eighth': 'eighth'
  };

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextButton(
          onPressed: () {
            setState(() {
              isMakingCustom = !isMakingCustom;
            });
          },
          child: const Text(
            "Custom Popular Search",
            style: TextStyle(
                fontStyle: FontStyle.italic,
                fontSize: 20.0,
                fontWeight: FontWeight.bold),
          ),
        ),
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
                widget.clCodes.length,
                (index) => Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: ChoiceChip.elevated(
                    label: Text(
                      widget.clCodes[index],
                      style: const TextStyle(fontSize: 12.0),
                    ),
                    selected: widget.clCodes[index] == selectedClCode,
                    onSelected: (value) {
                      setState(() {
                        selectedClCode = widget.clCodes[index];
                      });
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              const Padding(
                padding: EdgeInsets.all(8.0),
                child: Text(
                  'Choose grades',
                  style: TextStyle(
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.bold,
                    fontSize: 14.0,
                  ),
                ),
              ),
              ...List.generate(
                grades.length,
                (index) => Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: ChoiceChip.elevated(
                    label: Text(
                      grades[index],
                      style: const TextStyle(fontSize: 12.0),
                    ),
                    selected: selectedGrades
                        .any((element) => element == grades[index]),
                    onSelected: (value) {
                      setState(() {
                        if (value) {
                          selectedGrades.add(grades[index]);
                        } else {
                          selectedGrades.remove(grades[index]);
                        }
                      });
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              const Padding(
                padding: EdgeInsets.all(8.0),
                child: Text(
                  'Choose months',
                  style: TextStyle(
                    fontStyle: FontStyle.italic,
                    fontWeight: FontWeight.bold,
                    fontSize: 14.0,
                  ),
                ),
              ),
              ...List.generate(
                months.length,
                (index) => Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: ChoiceChip.elevated(
                    label: Text(
                      '${months[index]}',
                      style: const TextStyle(fontSize: 12.0),
                    ),
                    selected: selectedMonths
                        .any((element) => element == months[index]),
                    onSelected: (value) {
                      setState(() {
                        if (value) {
                          selectedMonths.add(months[index]);
                        } else {
                          selectedMonths.remove(months[index]);
                        }
                      });
                    },
                  ),
                ),
              ),
            ],
          ),
        ),
        Center(
          child: TextButton(
              onPressed: () {
                recommendMostPopular();
              },
              child: const Text("Recommend")),
        ),
        const Text(
          "Results",
          style: TextStyle(
              fontStyle: FontStyle.italic,
              fontSize: 20.0,
              fontWeight: FontWeight.bold),
        ),
        SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: List.generate(
                  mostPopulars.length,
                  (index) => Card(
                        child: Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              SelectableText(mostPopulars[index].name),
                              SelectableText(mostPopulars[index].uid),
                              Center(
                                child: TextButton.icon(
                                  label: const Text(
                                    "more info",
                                    style: TextStyle(fontSize: 12.0),
                                  ),
                                  icon: const Icon(Icons.info, size: 12.0),
                                  onPressed: () {
                                    showModalBottomSheet(
                                        context: context,
                                        builder: (context) {
                                          return PageSheetInfo(
                                              page: mostPopulars[index]);
                                        });
                                  },
                                ),
                              )
                            ],
                          ),
                        ),
                      )),
            )),
      ],
    );
  }

  void recommendMostPopular() async {
    final List<String> cl = selectedClCode.split("-");
    var cCode = cl[0], lCode = cl[1];
    var url = Uri.parse('http://127.0.0.1:5000/api/mostpopular');
    var body = jsonEncode({
      "filters": {
        "AgeFilter": {"ages": selectedGrades.map((e) => gradesMap[e]).toList()},
        "MonthFilter": {"months": selectedMonths}
      },
      "cCode": cCode,
      "lCode": lCode,
    });
    var headers = {"Content-Type": "application/json"};
    var response = await http.post(url, headers: headers, body: body);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      List<dynamic> data = json.decode(response.body);
      setState(() {
        mostPopulars = data.map((e) => MathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}
