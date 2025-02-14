import 'package:flutter/material.dart';
import 'dart:html';
import 'dart:js' as js;
import 'dart:ui' as ui;

void main() {
  runApp(const MyApp());
}

/// Application itself.
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      title: 'Image Viewer',
      home: HomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

/// [Widget] displaying the home page consisting of an image and the buttons.
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

/// State of a [HomePage].
class _HomePageState extends State<HomePage> {
  final TextEditingController _urlController = TextEditingController();
  String? _currentImageUrl;
  bool _isMenuOpen = false;
  DivElement? imageElement;

  // Create DOM container for the HTML image
  final String viewId = 'html-image-container';
  late final DivElement _htmlContainer;

  @override
  void initState() {
    super.initState();

    // Create the HTML container for the image
    _htmlContainer = DivElement()
      ..id = viewId
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.display = 'flex'
      ..style.justifyContent = 'center'
      ..style.alignItems = 'center';

    // Register the container
    // ignore: undefined_prefixed_name
    ui.platformViewRegistry.registerViewFactory(
      viewId,
      (int viewId) => _htmlContainer,
    );
  }

  void _loadImage() {
    if (_urlController.text.isNotEmpty) {
      setState(() {
        _currentImageUrl = _urlController.text;
      });

      // Clear existing content
      _htmlContainer.children.clear();

      // Create and add new image
      final img = ImageElement(src: _currentImageUrl)
        ..id = 'fullscreen-image'
        ..style.maxWidth = '100vw'
        ..style.maxHeight = '100vh'
        ..style.objectFit = 'contain';

      // Add double-click event for fullscreen toggle
      img.onDoubleClick.listen((_) {
        _toggleImageFullscreen();
      });

      _htmlContainer.children.add(img);
      imageElement = img as DivElement;
    }
  }

  void _toggleImageFullscreen() {
    // Don't use document.fullscreenElement directly, use the specific image element
    js.context.callMethod('eval', [
      '''
      var img = document.getElementById('fullscreen-image');
      if (img) {
        if (!document.fullscreenElement) {
          if (img.requestFullscreen) {
            img.requestFullscreen();
          }
        } else {
          if (document.exitFullscreen) {
            document.exitFullscreen();
          }
        }
      }
    '''
    ]);
  }

  void _enterImageFullscreen() {
    js.context.callMethod('eval', [
      '''
      var img = document.getElementById('fullscreen-image');
      if (img && !document.fullscreenElement) {
        if (img.requestFullscreen) {
          img.requestFullscreen();
        }
      }
    '''
    ]);
  }

  void _exitFullscreen() {
    js.context.callMethod('eval', [
      '''
      if (document.fullscreenElement) {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        }
      }
    '''
    ]);
  }

  void _toggleMenu() {
    setState(() {
      _isMenuOpen = !_isMenuOpen;
    });
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(32, 16, 32, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Expanded(
                  child: AspectRatio(
                    aspectRatio: 1,
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.grey.shade200,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      // Use HtmlElementView to display the HTML image
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: HtmlElementView(viewType: viewId),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _urlController,
                        decoration:
                            const InputDecoration(hintText: 'Image URL'),
                      ),
                    ),
                    ElevatedButton(
                      onPressed: _loadImage,
                      child: const Padding(
                        padding: EdgeInsets.fromLTRB(0, 12, 0, 12),
                        child: Icon(Icons.arrow_forward),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 64),
              ],
            ),
          ),
          // Overlay for dimming the background when menu is open
          Stack(
            children: [
              // Background dimming overlay when menu is open
              if (_isMenuOpen)
                Positioned.fill(
                  child: GestureDetector(
                    onTap: _toggleMenu, // Close the menu when tapping outside
                    child: Container(
                      color: Colors.black.withOpacity(0.5), // Dim effect
                    ),
                  ),
                ),

              // Floating button and menu
              Positioned(
                bottom: 15,
                right: 10,
                child: FloatingActionButton(
                  onPressed: _toggleMenu,
                  elevation: _isMenuOpen ? 10 : 6,
                  child: const Icon(Icons.add),
                ),
              ),

              if (_isMenuOpen)
                Positioned(
                  bottom: 80, // Adjusted to avoid overlapping the button
                  right: 10,
                  child: Material(
                    elevation: 8,
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      width: 180,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          InkWell(
                            onTap: () {
                              _enterImageFullscreen();
                              _toggleMenu();
                            },
                            child: Container(
                              width: double.infinity,
                              padding: const EdgeInsets.symmetric(
                                  vertical: 12, horizontal: 16,),
                              child: const Text('Enter fullscreen'),
                            ),
                          ),
                          const Divider(height: 1),
                          InkWell(
                            onTap: () {
                              _exitFullscreen();
                              _toggleMenu();
                            },
                            child: Container(
                              width: double.infinity,
                              padding: const EdgeInsets.symmetric(
                                  vertical: 12, horizontal: 16,),
                              child: const Text('Exit fullscreen'),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
