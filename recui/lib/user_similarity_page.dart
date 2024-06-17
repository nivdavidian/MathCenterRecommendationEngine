import 'dart:convert';
import 'dart:developer';

import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:recui/json_classess.dart';

class UserSimilarityPage extends StatefulWidget {
  const UserSimilarityPage({super.key});

  @override
  State<UserSimilarityPage> createState() => _UserSimilarityPageState();
}

class _UserSimilarityPageState extends State<UserSimilarityPage> {
  var chosenHistory = List<MathCenterPage>.empty(growable: true);
  var pages = List<MathCenterPage>.empty(growable: true);

  var searchString = "";

  var isLoading = false;

  var clCodes = List<String>.empty(growable: true);

  var selectedClCode = '';

  @override
  void initState() {
    super.initState();
    getClCodes();
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

  void updateChosenHistory(List<MathCenterPage> chosenHistory) {
    setState(() {
      chosenHistory = chosenHistory;
    });
  }

  void addChosen(MathCenterPage page) {
    setState(() {
      chosenHistory.add(page);
    });
  }

  void removeChosen(MathCenterPage page) {
    setState(() {
      chosenHistory.removeWhere((item) => item.uid == page.uid);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Similarity Page"),
      ),
      body: Stack(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
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
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    flex: 2,
                    child: SearchBar(
                      trailing: [
                        IconButton(
                          icon: const Icon(Icons.search),
                          onPressed: () {
                            var splitCl = selectedClCode.split("-");
                            var cCode = splitCl[0], lCode = splitCl[1];
                            searchPage(searchString, cCode, lCode);
                          },
                        )
                      ],
                      hintText: "Search Page",
                      elevation: MaterialStateProperty.all(10.0),
                      onChanged: (value) {
                        searchString = value;
                      },
                      onSubmitted: (value) {
                        var splitCl = selectedClCode.split("-");
                        var cCode = splitCl[0], lCode = splitCl[1];
                        searchPage(searchString, cCode, lCode);
                      },
                    ),
                  ),
                  const SizedBox(
                    width: 20,
                  ),
                  TextButton(
                      onPressed: () {
                        Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => HistoryPage(
                                  chosenHistory: chosenHistory,
                                  updateChosen: updateChosenHistory),
                            ));
                      },
                      child: const Text("History"))
                ],
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
                            (index) => PageTile(
                                  page: pages[index],
                                  addChosen: addChosen,
                                  removeChosen: removeChosen,
                                  selected: chosenHistory.any((element) =>
                                      element.uid == pages[index].uid),
                                )),
                      ),
                    ),
            ],
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: FittedBox(
              fit: BoxFit.scaleDown,
              child: TextButton(
                onPressed: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) =>
                              UserSimilarityRecommendationPage(
                                  chosenHistory: chosenHistory,
                                  clCode: selectedClCode)));
                },
                style: ButtonStyle(
                  backgroundColor: MaterialStateProperty.all(Colors.pink[100]),
                  elevation: MaterialStateProperty.all(50.0),
                  shadowColor: MaterialStateProperty.all(Colors.black),
                  minimumSize: MaterialStateProperty.all(
                    const Size(150, 50),
                  ),
                ),
                child: const Text("Start Recommending"),
              ),
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
}

class PageTile extends StatefulWidget {
  const PageTile(
      {super.key,
      required this.page,
      required this.addChosen,
      required this.removeChosen,
      required this.selected});
  final MathCenterPage page;
  final Function addChosen;
  final Function removeChosen;
  final bool selected;

  @override
  State<PageTile> createState() => _PageTileState();
}

class _PageTileState extends State<PageTile> {
  @override
  Widget build(BuildContext context) {
    var page = widget.page;
    return Row(
      children: [
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(5.0),
            child: ListTile(
              selectedTileColor: Colors.pink[50],
              selected: widget.selected,
              title: Text(page.name),
              subtitle: Text(page.uid),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(7.0),
              ),
              // tileColor: Colors.amber,
              onTap: () {},
            ),
          ),
        ),
        IconButton(
            onPressed: () {
              widget.removeChosen(page);
            },
            icon: const Icon(Icons.remove)),
        IconButton(
            onPressed: () {
              widget.addChosen(page);
            },
            icon: const Icon(Icons.add))
      ],
    );
  }
}

class HistoryPage extends StatefulWidget {
  const HistoryPage(
      {super.key, required this.chosenHistory, required this.updateChosen});
  final List<MathCenterPage> chosenHistory;
  final Function updateChosen;

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("My History"),
      ),
      body: ListView(
        children: List.generate(
          widget.chosenHistory.length,
          (index) => ListTile(
            onTap: () {},
            title: Text(widget.chosenHistory[index].name),
            subtitle: Text(widget.chosenHistory[index].uid),
            trailing: IconButton(
              icon: const Icon(Icons.remove),
              onPressed: () {
                setState(() {
                  widget.chosenHistory.removeAt(index);
                });
                widget.updateChosen(widget.chosenHistory);
              },
            ),
          ),
        ),
      ),
    );
  }
}

class UserSimilarityRecommendationPage extends StatefulWidget {
  const UserSimilarityRecommendationPage(
      {super.key, required this.chosenHistory, required this.clCode});

  final List<MathCenterPage> chosenHistory;
  final String clCode;

  @override
  State<UserSimilarityRecommendationPage> createState() =>
      _UserSimilarityRecommendationPageState();
}

class _UserSimilarityRecommendationPageState
    extends State<UserSimilarityRecommendationPage> {
  var isFolded = true;
  var recommendations = List<MathCenterPage>.empty(growable: true);
  var isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchRecommendations();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Recommedation - User Similarity"),
      ),
      body: isLoading
          ? const CircularProgressIndicator()
          : Column(
              children: [
                Row(
                  children: [
                    TextButton.icon(
                      onPressed: () {
                        setState(() {
                          isFolded = !isFolded;
                        });
                      },
                      icon: isFolded
                          ? const Icon(Icons.arrow_forward_ios)
                          : const Icon(Icons.arrow_back_ios),
                      label: const Text("History"),
                    ),
                    Expanded(
                      child: SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: isFolded
                              ? [const SizedBox()]
                              : List.generate(
                                  widget.chosenHistory.length,
                                  (index) => TextButton(
                                    onPressed: () {
                                      showModalBottomSheet(
                                          context: context,
                                          builder: (context) {
                                            return PageSheetInfo(
                                                page: widget
                                                    .chosenHistory[index]);
                                          });
                                    },
                                    child:
                                        Text(widget.chosenHistory[index].name),
                                  ),
                                ),
                        ),
                      ),
                    )
                  ],
                ),
                Expanded(
                  child: ListView(
                    children: List.generate(
                        recommendations.length,
                        (index) => Padding(
                              padding: const EdgeInsets.all(5.0),
                              child: ListTile(
                                title: Text(recommendations[index].name),
                                subtitle: Text(recommendations[index].uid),
                                onTap: () {
                                  showModalBottomSheet(
                                      context: context,
                                      builder: (context) {
                                        return PageSheetInfo(
                                            page: recommendations[index]);
                                      });
                                },
                              ),
                            )),
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

    var url = Uri.parse('https://nivres.com/api/recuseralike');
    var body = jsonEncode({
      "already_watched": [],
      "worksheet_uids": (widget.chosenHistory.map((e) => e.uid).toList()),
      "cCode": cCode,
      "lCode": lCode,
    });
    var headers = {"Content-Type": "application/json"};
    var response = await http.post(url, body: body, headers: headers);
    var data = List<dynamic>.empty(growable: true);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      data = json.decode(response.body);

      setState(() {
        isLoading = false;
        recommendations = data.map((e) => MathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}

class PageSheetInfo extends StatelessWidget {
  const PageSheetInfo({
    super.key,
    required this.page,
  });

  final MathCenterPage page;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SelectableText(
            page.name,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          SelectableText(
            'UID: ${page.uid}',
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 8),
          SelectableText(
            'Grade Range: ${page.minGrade} - ${page.maxGrade}',
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 8),
          const SelectableText(
            'Topics:',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          for (var topic in page.topics)
            SelectableText(
              '- $topic',
              style: const TextStyle(fontSize: 16),
            ),
        ],
      ),
    );
  }
}
