import 'dart:convert';
import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:recui/json_classess.dart';
import 'package:recui/user_similarity_page.dart';

class MixedPage extends StatefulWidget {
  const MixedPage({super.key});

  @override
  State<MixedPage> createState() => _MixedPageState();
}

class _MixedPageState extends State<MixedPage> {
  var _us_score_controller = TextEditingController();
  var us_score = 0.3;

  var _markov_score_controller = TextEditingController();
  var markov_score = 0.4;

  var _ps_score_controller = TextEditingController();
  var ps_score = 0.25;

  var _mp_score_controller = TextEditingController();
  var mp_score = 0.05;

  var isLoading = false;

  var clCodes = List<String>.empty(growable: true);

  var pages = List<MathCenterPage>.empty(growable: true);

  var selectedClCode = '';

  @override
  void initState() {
    super.initState();

    _us_score_controller = TextEditingController();
    _us_score_controller.text = us_score.toString();

    _markov_score_controller = TextEditingController();
    _markov_score_controller.text = markov_score.toString();

    _ps_score_controller = TextEditingController();
    _ps_score_controller.text = ps_score.toString();

    _mp_score_controller = TextEditingController();
    _mp_score_controller.text = mp_score.toString();
    getClCodes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mixed Model'),
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
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                Container(
                  width: 200,
                  height: 70,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: TextField(
                      controller: _us_score_controller,
                      decoration: const InputDecoration(
                          hintText: "UserSimilarity Score",
                          labelText: "UserSimilarity Score"),
                      onChanged: (value) {
                        us_score = double.parse(value);
                      },
                    ),
                  ),
                ),
                Container(
                  width: 200,
                  height: 70,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: TextField(
                      controller: _markov_score_controller,
                      decoration: const InputDecoration(
                        hintText: "Markov Score",
                        labelText: "Markov Score",
                      ),
                      onChanged: (value) {
                        markov_score = double.parse(value);
                      },
                    ),
                  ),
                ),
                Container(
                  width: 200,
                  height: 70,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: TextField(
                      controller: _ps_score_controller,
                      decoration: const InputDecoration(
                        hintText: "PageSimilarity Score",
                        labelText: "PageSimilarity Score",
                      ),
                      onChanged: (value) {
                        ps_score = double.parse(value);
                      },
                    ),
                  ),
                ),
                Container(
                  width: 200,
                  height: 70,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: TextField(
                      controller: _mp_score_controller,
                      decoration: const InputDecoration(
                          hintText: "MostPopular Score",
                          labelText: "MostPopular Score"),
                      onChanged: (value) {
                        mp_score = double.parse(value);
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
                                            MixedRecommendationPage(
                                                page: pages[index],
                                                clCode: selectedClCode,
                                                markovScore: markov_score,
                                                usScore: us_score,
                                                psScore: ps_score,
                                                mpScore: mp_score)));
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

class MixedRecommendationPage extends StatefulWidget {
  const MixedRecommendationPage(
      {super.key,
      required this.page,
      required this.clCode,
      required this.markovScore,
      required this.usScore,
      required this.psScore,
      required this.mpScore});
  final MathCenterPage page;
  final String clCode;
  final double markovScore;
  final double usScore;
  final double psScore;
  final double mpScore;
  @override
  State<MixedRecommendationPage> createState() =>
      _MixedRecommendationPageState();
}

class _MixedRecommendationPageState extends State<MixedRecommendationPage> {
  var isLoading = true;
  var recommendations = List<MixedRecMathCenterPage>.empty(growable: true);
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
        title: const Text('Mixed Recommendations'),
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
                                  onTap: () {
                                    showModalBottomSheet(
                                        context: context,
                                        builder: (context) =>
                                            MixedPageSheetInfo(
                                              page: recommendations[index],
                                              markovScore: widget.markovScore,
                                              usScore: widget.usScore,
                                              psScore: widget.psScore,
                                              mpScore: widget.mpScore,
                                            ));
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

    var url = Uri.parse('https://nivres.com/api/recmodel');
    var body = jsonEncode({
      "uids": [widget.page.uid],
      "cCode": cCode,
      "lCode": lCode,
      "grade": [
        gradesMap[widget.page.minGrade],
        gradesMap[widget.page.maxGrade]
      ],
      "markov_score": widget.markovScore,
      "us_score": widget.usScore,
      "ps_score": widget.psScore,
      "mp_score": widget.mpScore,
      // "n": 10,
    });

    print(body);
    var headers = {"Content-Type": "application/json"};
    var response = await http.post(url, body: body, headers: headers);
    var data = List<dynamic>.empty(growable: true);
    if (response.statusCode == 200) {
      // If the server returns a 200 OK response, then parse the JSON.
      data = json.decode(response.body);

      setState(() {
        isLoading = false;
        recommendations =
            data.map((e) => MixedRecMathCenterPage.fromJson(e)).toList();
      });
    } else {
      // If the server did not return a 200 OK response,
      // then throw an exception.
      log("${response.statusCode}");
    }
  }
}

class MixedPageSheetInfo extends StatelessWidget {
  const MixedPageSheetInfo(
      {super.key,
      required this.page,
      required this.markovScore,
      required this.usScore,
      required this.psScore,
      required this.mpScore});

  final MixedRecMathCenterPage page;

  final double markovScore;
  final double usScore;
  final double psScore;
  final double mpScore;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: SingleChildScrollView(
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
            const SizedBox(height: 8),
            SelectableText(
              'Score: ${page.score}',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 8),
            SelectableText(
              'Markov Score: ${page.markovScore / markovScore}',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 8),
            SelectableText(
              'User Similarity Score: ${page.userSimilarityScore / usScore}',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 8),
            SelectableText(
              'Page Similarity Score: ${page.pageSimilarityScore / psScore}',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 8),
            SelectableText(
              'Most Popular Score: ${page.mostPopularScore / mpScore}',
              style: const TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}
